import os
import sys
import time
import serial
import pickle
import threading

from yaml import safe_load

from datetime import datetime, timezone

from astropy import units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation, SkyCoord, AltAz, Angle

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from observational_scheduler.obs_scheduler import target
from logger.astro_logger import astroLogger

parentPath = os.path.dirname(__file__).replace('/mount', '')


def request_mount_command():
    ### Recieve a command from moxa-pocs/core by loading the pickle instance it has provided in the pickle directory
    with open(f"{parentPath}/pickle/current_target.pickle", "rb") as f:
        current_target = pickle.load(f)

    logger.debug(f"Read current_target.pickle and recieved: {current_target}")

    return current_target

def sendTargetObjectCommand(current_target_object, cmd):
    ### Send a command to other modules via current_target.pickle
    current_target_object.cmd = cmd
    with open(f"{parentPath}/pickle/current_target.pickle", "wb") as f:
        pickle.dump(current_target_object, f)
    logger.debug(f"Sent the following command to current_target.pickle: {cmd}")

def convertAltAztoRaDec(location, az, alt):
    # Az/Alt - astropy input strings in degrees (ex. "90d")
    observationTime = Time(datetime.now(timezone.utc))
    ParkPosLocal = AltAz(az=Angle(az), alt=Angle(alt), location=location, obstime=observationTime)

    return SkyCoord(ParkPosLocal).transform_to('icrs')

def get_mount_port():

    logger.debug("Sending initialization serial handshake to all ttyUSB* ports.")

    usbList = os.popen('ls /dev/ttyUSB*').read()
    usbList = usbList.split('\n')
    usbList.remove('')

    for usbPort in usbList:
        print(usbPort)
        with serial.Serial(usbPort, 115200, timeout=10) as mount:
            mount.write(b':MountInfo#')
            out = mount.read(4)
            logger.debug(f"Serial response from {usbPort} is {out}")
            if out == b'0040':
                logger.debug(f"Found mount on {usbPort}!")
                return mount
    
    logger.critical("Mount not found.")
    raise Exception("Failed to find mount. Possibly bad serial communication. Required mount for this software is the CEM40 from iOptron.")

def connect_to_mount():

    logger.info("Trying to connect to the mount.")

    mountSerialPort = get_mount_port()
    if not mountSerialPort.is_open:
                mountSerialPort.open()
    
    # Set the mount to slew at max speed, which is 1440 x Sidereal
    mountSerialPort.write(b':SR9#')
    out = mountSerialPort.read(1)
    logger.debug(f"Requested to set slewing to max speed, response: {out}")

    # Check that the slewing rate is its max, and set it if it isn't
    mountSerialPort.write(b':GSR#')
    slewingSpeed = mountSerialPort.read(2)
    if slewingSpeed != b'9#':
        print("Incorrect slewing rate, attempting to set it to 1440x sidereal")
        mountSerialPort.write(b':MSR9#')
        if mountSerialPort.read(1) == b'1':
            print("Succesfully updated slewing rate.")
        else:
            raise Exception("Problem setting sidereal tracking rate to 1440x sidereal")
    
    if mountSerialPort != None:
        logger.info("Connected to mount.")
    return mountSerialPort

def getCurrentSkyCoord(port):
    ### Returns a SkyCoord object of whatever the mount thinks it's currently pointing at (polar alignment required) ###
    logger.debug("Getting the current RA/DEC coordinates of the mount.")
    port.write(b':GEP#')
    rawPosition = port.read(18).decode('utf-8')
    rawDEC, rawRA = float(rawPosition[0:9]), float(rawPosition[9:17]) #(0.01 arcseconds, milliseconds)
    RADecimalDegree = Angle(str(rawRA * 1/100 + 's')).deg
    DECDecimalDegree = Angle(str(rawDEC * 1/100) + 's').deg
    
    logger.debug(f"{RADecimalDegree=}     {DECDecimalDegree=}")
    
    return SkyCoord(RADecimalDegree, DECDecimalDegree, unit=u.deg)

def park_slewToTarget(coordinates, mountSerialPort):
    '''
        Slew to a target. This is very inacurate, it uses the slewing rate to figure out how long it should slew for.
        This method is the equivalent of hitting the buttons on the hand controller, it works well for parking though.

        Inputs:
            coordinates
                An astropy SkyCoord object with the desired final coordinates

            mountSerialPort
                A serial.Serial object representing the mount    
    '''

    if not mountSerialPort.is_open:
        mountSerialPort.open()
    mountSerialPort.write(b':MH#')
    _ = mountSerialPort.read()
    logger.debug(f"Park slew: Response to go home request: {_}")

    time.sleep(20)

    if not mountSerialPort.is_open:
        mountSerialPort.open()
    mountSerialPort.write(b':SZP#')
    _ = mountSerialPort.read()
    logger.debug(f"Park slew: Response to set zero position request: {_}")

    currentCordinates = getCurrentSkyCoord(mountSerialPort)

    RADifference = (coordinates.ra.deg - currentCordinates.ra.deg + 180) % 360 - 180

    if RADifference < 0:
        ra_cmd = b':me#'
    elif RADifference > 0:
        ra_cmd = b':mw#'
    else:
        ra_cmd = ''
    
    # sidereal rate = 1440 * 15.042 arcseconds / seconds
    # 1440 is the multiple selected by :SR9# on an iEQ30Pro
    # 3600 arcseconds = 1 degree
    # (1 degree / 3600 arcseconds) * (15.042 arcseconds/ seconds)
    # = (1440 * 15.042) degrees / 3600 seconds = 6.0168
    # (RA difference degrees) / { degrees/second  }
    ra_time = abs(RADifference) / (6.0168)

    ### RA Movement ###
    ra_start_time = time.time()
    logger.info(f"Sending serial command: {ra_cmd}. Slewing RA axis to park position with desired execution time of {ra_time} seconds")
    mountSerialPort.write(ra_cmd)
    while (ra_start_time + ra_time + 5) > time.time():
        
        if ra_start_time + ra_time <= time.time():
            mountSerialPort.write(b':qR#')
            _ = mountSerialPort.read()
            logger.info(f"Sent serial command ':qR#'. Stoped slewing RA axis with an execution time of {time.time() - ra_start_time} seconds")
            break
    mountSerialPort.write(b':ST0#')
    _ = mountSerialPort.read()
    logger.info("Tracking stopped on RA axis.")
    logger.debug(f"Response to request to stop tracking: {_}")

    currentCordinates = getCurrentSkyCoord(mountSerialPort)

    DECDifference = coordinates.dec.deg - currentCordinates.dec.deg

    if DECDifference > 0:
        dec_cmd = b':mn#'
    elif DECDifference < 0:
        dec_cmd = b':ms#'
    else:
        dec_cmd = ''

    dec_time = abs(DECDifference) / (6.0168)

    ### DEC Movement ###
    dec_start_time = time.time()
    with mountSerialPort:
        logger.info(f"Sending serial command: {dec_cmd}. Slewing DEC axis to park position with desired execution time of {dec_time} seconds")
        mountSerialPort.write(dec_cmd)
        while (dec_start_time + dec_time + 5) > time.time():

            if dec_start_time + dec_time <= time.time():
                mountSerialPort.write(b':qD#')
                _ = mountSerialPort.read()
                logger.info(f"Sent serial command ':qD#'. Stopped DEC slewing with an execution time of {time.time() - dec_start_time} seconds")
                logger.info(f"Response to request to stop slewing the DEC axis: {_}")
                break

def slewToTarget(coordinates, mountSerialPort=None):
    '''
        Slews to coordinates, from a parked states.

        coordinates is a astropy SkyCoord object

        mountSerialPort is a serial.Serial object representing the mount

    '''

    if not mountSerialPort.is_open:
         mountSerialPort.open()
    mountSerialPort.write(b':MP0#')
    _ = mountSerialPort.read()
    mountSerialPort.write(b':MH#')
    _ = mountSerialPort.read()
    logger.debug(f"Result of go to home request: {_}")
    logger.info("Waiting for mount to reach the home position.")

    time.sleep(20)

    # Format desired coordinates into serial commands
    RA_string = str(round(coordinates.ra.deg * 60 * 60 * 100))
    NumZeros = max(0, 9 - len(RA_string))
    RA_CentiArcseconds = "0" * NumZeros + RA_string

    val = round(coordinates.dec.deg * 60 * 60 * 100)
    NumZeros = max(0, 8 - len(str(val)))
    if val >= 0:
        DEC_SignedCentiArcseconds = "+" + "0" * NumZeros + str(val)
    else:
        DEC_SignedCentiArcseconds = "-" + "0" * NumZeros + str(val)

    RA_cmd = f':SRA{RA_CentiArcseconds}#'.encode()
    DEC_cmd = f':Sd{DEC_SignedCentiArcseconds}#'.encode()

    logger.debug(f"{RA_cmd=}      {DEC_cmd=}")

    if not mountSerialPort.is_open:
         mountSerialPort.open()
    mountSerialPort.write(RA_cmd)
    _ = mountSerialPort.read()
    logger.debug(f"Result of sending the RA_cmd: {_}")
    mountSerialPort.write(DEC_cmd)
    _ = mountSerialPort.read()
    logger.debug(f"Result of sending the DEC_cmd: {_}")
    mountSerialPort.write(b':MS1#')
    _ = mountSerialPort.read()
    logger.info("Slewing to target.")
    logger.debug(f"Result of sending the slew command: {_}")
    time.sleep(30)

    if _ == b"0":
        return False

    elif _ == b"1":
        time.sleep(30)
        return True

def park(mountSerialPort, location):
    '''
    Parks the mount from any position. Works by converting the alt-az coordinates that represent
    looking down at the ground with the weather proofing up into equitorial coordinates and calling
    the old slew to target function, which takes a delta of equitorial coordinates and calculates 
    slew times. It was not accurate enough for slewing to actual targets, but works well for parking.

    mountSerialPort - serial.Serial object representing the mount

    '''

    logger.info("Parking the mount.")

    parkPosition = convertAltAztoRaDec(location, "90d", "-90d")

    if not mountSerialPort.is_open:
        mountSerialPort.open()

    park_slewToTarget(parkPosition, mountSerialPort)

    logger.info("Done parking the mount.")

def correctTracking(mountSerialPort, coordinates, astrometryAPI, abortOnFailedSolve):
    '''
     This function is responsible for converting the latest image into a .jpg, uploading it to
     astrometry.net, recieving the plate solved response, and executing a tracking correction 
     on the mount.
     Inputs:
            mountSerialPort
              A serial.Serial object connected to the mount
            
            coordinates:
              An astropy SkyCoord object
            
            astrometryAPI
              An API key specified in settings.yaml, so that an owner of the unit
              can see what images are being plate solved in real time from their 
              dashboard on astrometry.net

            abortOnFailedSolve (not yet implemented)
              A bool that is used to determine what to do after an image comes back
              with a 'failure' status from the astrometry.net API. Unsolvable images
              are of no scientific value to project PANOTPES.
    '''
    if astrometryAPI in (None, "None", 0, False):
        logger.info("Skipping plate solving as directed by the PLATE_SOLVE setting.")
        return
    
    import json
    import random
    import ssl # Need this for the moxa build, consider making into raspbian and moxa packages bc of security risks
    
    from urllib import request, parse

    def setTrackingSettings():
        '''
        Sets mount guiding to maximum speed and returns what the mount actually says its guiding rate is for redundancy.
        Output:
            RAGuideRate, DECGuideRate
        '''
        # Set mount guide rate to max value
        if not mountSerialPort.is_open:
            mountSerialPort.open()
        mountSerialPort.write(b':RG9099')
        _ = mountSerialPort.read(1)
        logger.debug(f"Mount response to setting guiding rates: {_}")

        # Confirm guiding rate took effect
        mountSerialPort.write(b':AG#')
        out = mountSerialPort.read(5).decode('utf-8')
        RAGuideRate = float('0.' + out[0:1])  # 0.XX * sidereal, min rate = 0.01, max rate = 0.90
        DECGuideRate = float('0.' + out[2:3]) # 0.XX * sidereal, min rate = 0.10, max rate = 0.99
        logger.debug(f"Mount reported guiding rates: {RAGuideRate=}  {DECGuideRate=}")
        return RAGuideRate, DECGuideRate

    def getCurrentImageFolder():
        # Find most recent observation directory
        time.sleep(5) # Let camera module make observation folder
        dates = []
        format = "%Y-%m-%d_%H:%M:%S"
        for fileName in os.listdir(f"{parentPath}/images"):
            try:
                dates.append(datetime.strptime(fileName, format))
            except Exception:
                pass

        currentImageFolder = datetime.strftime(max(dates), format)
        logger.debug(f"Found the most recent observation folder: {parentPath}/images/{currentImageFolder}")

    def getNewestImages(previousRawImages):
        # Find the most recent image in the most recent observation folder, search for the first image until a timeout period of 5 minutes
        logger.debug("Waiting for new raw images...")
        timeout = time.time() + 60 * 5
        waitForNewImage = True
        while waitForNewImage:
            rawImages = []
            for dir, subdir, files in os.walk(f"{parentPath}/images/{currentImageFolder}"):
                for file in files:
                    if os.path.splitext(file)[1].lower() in ('.cr2', '.thumb.jpg'):
                        rawImages.append(os.path.join(dir, file))

            newRawImages = list(set(previousRawImages).symmetric_difference(set(rawImages)))
            previousRawImages = rawImages

            try:
                rawImage = newRawImages[-1]
                logger.debug("Found new raw images.")
                return rawImage, previousRawImages
            except IndexError:
                pass

            if time.time() > timeout:
                logger.warning("Plate-solve timeout reached waiting for new image from camera module. (System is hardcoded to wait 5minutes for an image after calling the camera module)")
                return

            time.sleep(1)

    def plateSolveWithAPI():
        '''
        Wrangles the astrometry API to plate solve the .thumb.jpg. Returns an (RA, DEC) touple
        '''

        logger.debug("Logging into astrometry.net through the API.")
        data = parse.urlencode({'request-json': json.dumps({"apikey": astrometryAPI})}).encode()
        loginRequest = request.Request('http://nova.astrometry.net/api/login', data=data)
        response = json.loads(request.urlopen(loginRequest).read())

        if response['status'] == "success":
            logger.debug("Logged in successfully.")

            session_id = response['session']
            logger.debug(f"Session ID: {session_id}")

            # File uploading, taken from astrometry.net's API documentation and github client
            f = open(rawImage.replace(".cr2", ".thumb.jpg"), 'rb')
            file_args = (rawImage.replace(".cr2", ".thumb.jpg"), f.read())

            boundary_key = ''.join([random.choice('0123456789') for i in range(19)])
            boundary = '===============%s==' % boundary_key
            headers = {'Content-Type':
                        'multipart/form-data; boundary="%s"' % boundary}
            
            data_pre = (
                '--' + boundary + '\n' +
                'Content-Type: text/plain\r\n' +
                'MIME-Version: 1.0\r\n' +
                'Content-disposition: form-data; name="request-json"\r\n' +
                '\r\n' +
                json.dumps({'session': session_id}) + '\n' +
                '--' + boundary + '\n' +
                'Content-Type: application/octet-stream\r\n' +
                'MIME-Version: 1.0\r\n' +
                'Content-disposition: form-data; name="file"; filename="%s"' % file_args[0] +
                '\r\n' + '\r\n')
            data_post = (
                '\n' + '--' + boundary + '--\n')
            data = data_pre.encode() + file_args[1] + data_post.encode()

            fileUploadRequest = request.Request(url='http://nova.astrometry.net/api/upload', headers=headers, data=data)
            response = json.loads(request.urlopen(fileUploadRequest).read())

            submission_id = response['subid']
            logger.info("Uploaded image to astrometry.net for plate solving.")
            logger.debug(f"submission_id = {submission_id}")

            logger.debug("Waiting for file to start being plate solved...")
            timeout = time.time() + 60 * 5
            waitForQue = True
            while waitForQue:
                time.sleep(1)

                gcontext = ssl.SSLContext() # Again, needed on the moxa system

                jobIDRequest = request.Request(url='https://nova.astrometry.net/api/submissions/' + str(submission_id))
                response = json.loads(request.urlopen(jobIDRequest, context=gcontext).read())
                logger.debug(f"jobIDRequest response: {response}")

                try:
                    jobID = response['jobs'][0]
                    if jobID is not None:
                        logger.debug("Plate solving started.")
                        break
                except IndexError:
                    pass

                if time.time() > timeout:
                    logger.warning("Plate-solve timeout reached waiting for astronomy.net to begin plate solving image.")
                    return

            logger.debug("Waiting for astrometry.net to plate solve...")
            timeout = time.time() + 60 * 10
            waitForPlateSolve = True
            while waitForPlateSolve:
                plateSolveStatusRequest = request.Request(url='https://nova.astrometry.net/api/jobs/' + str(submission_id))
                response = json.loads(request.urlopen(plateSolveStatusRequest, context=gcontext).read())

                if response["status"] == "success":
                    logger.info("Image has been successfully plate solved.")
                    break
                elif response["status"] == "failure":
                    logger.warning("Unable to plate solve image.")
                    return False, False
                elif time.time() > timeout:
                    logger.warning("Plate-solve timeout reached waiting for astronomy.net to plate solve the image.")
                    return
                
                time.sleep(1)
            
            timeout = time.time() + 60 * 10
            waitForImageData = True
            while waitForImageData:
                time.sleep(1)
                    
                imageCoordinatesRequest = request.Request(url='https://nova.astrometry.net/api/jobs/' + str(jobID) + '/calibration')
                response = json.loads(request.urlopen(imageCoordinatesRequest, context=gcontext).read())

                try:
                    RADecimal = response['ra']
                    DECDecimal = response['dec']

                    logger.debug(f"Plate solve coordinates: ra: {RADecimal} dec: {DECDecimal}")
                    return RADecimal, DECDecimal
                except KeyError as e:
                    pass

                if time.time() > timeout:
                    logger.warning("Plate-solve timeout reached waiting for astronomy.net to publish image data.")
                    return

        else:
            logger.warning("Problem logging into the astrometry.net API! Check your API key and internet connection.")

    def executeTrackingCorrection():
        # Perform guiding - aka tracking correction
        RACorrection = RADecimal - coordinates.ra.deg
        DECCorrection = DECDecimal - coordinates.dec.deg

        if RACorrection < 0:
            RAGuidePre = ':ZQ'
        elif RACorrection > 0:
            RAGuidePre = ':ZS'

        if DECCorrection > 0:
            DECGuidePre = ':ZE'
        elif DECCorrection < 0:
            DECGuidePre = ':ZC'

        # sidereal tracking rate = 15.041 arcseconds / second 
        # sidereal tracking rate = 15.041 / 3600  degrees / second
        # Guide rate = RADECGuideRate * 15.041 / 3600 degrees / second
        # Guide rate = RADECGuideRate * 15.041 / (3600 * 1000) degrees / milliseconds

        RAGuideTime = RACorrection / ((RAGuideRate) * 15.041 / 3600000)
        DECGuideTime = DECCorrection / (DECGuideRate * 15.041 / 3600000)
        logger.debug(f"Calculated guide times of: ra: {RAGuideTime}ms dec: {DECGuideTime}ms")

        if not mountSerialPort.is_open:
            mountSerialPort.open()

        if RAGuideTime > 100:
            if RAGuideTime > 99999:
                cmdRAData = str(99999)
            else:
                RAGuideTime = str(round(abs(RAGuideTime)))
                cmdRAData = "0" * (5 - len(RAGuideTime)) + RAGuideTime

            RAcmd = RAGuidePre + cmdRAData + '#'
            mountSerialPort.write(bytes(RAcmd))
            logger.debug(f"Sent the RA guide command {RAcmd} to the mount.")



        if DECGuideTime > 100:
            if DECGuideTime > 99999:
                cmdDECData = str(99999)
            else:
                DECGuideTime = str(round(abs(DECGuideTime)))
                cmdDECData = "0" * (5 - len(DECGuideTime)) + DECGuideTime

            DECcmd = DECGuidePre + cmdDECData + '#'
            mountSerialPort.write(bytes(DECcmd))
            logger.debug(f"Sent the DEC guide command {DECcmd} to the mount")

        logger.info("Succesfully executed necessary tracking corrections.")
        time.sleep(100)

    ### Start of correctTracking() ### 
    try:

        RAGuideRate, DECGuideRate = setTrackingSettings()

        currentImageFolder = getCurrentImageFolder()

        previousRawImages = []
        camerasObserving = True
        while camerasObserving:
            rawImage, previousRawImages = getNewestImages(previousRawImages)

            start = time.time() # Time how long it takes to get actual coordinates after taking an image for logging and understanding how plate solve time impacts guiding
            logger.info("Correcting tracking by plate solving...")

            # Convert newest .cr2 into a .jpg
            os.system(f"dcraw -e {rawImage}")
            logger.debug(f"Converted {rawImage} to .thumb.jpg")

            RADecimal, DECDecimal = plateSolveWithAPI()

            if RADecimal is not False: # RADecimal == False if plate solving fails
            
                logger.debug(f"Time spent calculating correction: {time.time() - start}")

                executeTrackingCorrection()
            
            if abortOnFailedSolve and RADecimal == False:
                # TODO: Decide and implement one of the following:
                #          1. Go to the next target
                #          2. Wait X minutes and try again (cloud cover, starlink satelite, whatever)
                #          3. Fully turn off the system
                #          4. Remove this feature and just continue to try and plate solve
                pass

    except Exception as e:
        logger.error("Error during plate solving:", e)

def main():

    logger.info("Mount module activated.")

    PARENT_DIRECTORY = os.path.dirname(__file__).replace('/mount', '')

    with open(f"{PARENT_DIRECTORY}/conf_files/settings.yaml", 'r') as f:
        settings = safe_load(f)
    logger.debug(f"Read system settings with values: {settings}")

    LAT_CONFIG = settings['LATITUDE']
    LON_CONFIG = settings['LONGITUDE']
    ELEVATION_CONFIG = settings['ELEVATION']
    UNIT_LOCATION = EarthLocation(lat=LAT_CONFIG, lon=LON_CONFIG, height=ELEVATION_CONFIG * u.m)
    ASTROMETRY_API = settings['PLATE_SOLVE']
    ABORT_FAILED_SOLVE_ATTEMPT = settings['ABORT_AFTER_FAILED_SOLVE']

    mount_port = connect_to_mount()

    ### Start main mount loop that listens for incoming command from moxa-pocs/core and executes as necessary
    logger.debug("Mount main loop activated.")
    while True:
    
        time.sleep(1)

        current_target = request_mount_command()

        if not mount_port.is_open:
            mount_port.open()

        match current_target.cmd:

            case 'slew to target':
                print("System attempting to slew to target...")
                logger.info("Getting ready to slew to target.")

                mount_port.write(b':MP0#') # command has no effect if already unparked
                _ = mount_port.read()
                logger.debug(f"Result of unpark command: {_}")

                coordinates = SkyCoord(current_target.position['ra'], current_target.position['dec'], unit=(u.hourangle, u.deg))
                acceptedSlew = slewToTarget(coordinates, mount_port)

                if not acceptedSlew:
                    logger.warning("Mount did not accept slew command. Parking mount, system will try observing next target.")
                    print("Mount will not slew to target because of altitude or mechanical limits. Aborting observation of this target.")
                    print("By default, the mounts altitude limit is set to +30 degrees. You can change it using the hand controller.")

                    park(mount_port, UNIT_LOCATION)
                    sendTargetObjectCommand(current_target, 'parked')
                    time.sleep(2)
                    mount_port.close()
                    logger.debug("Closed the mount's serial port.")
                    break

                elif acceptedSlew:
                    current_target = request_mount_command()
                    sendTargetObjectCommand(current_target, 'parked')
                    sendTargetObjectCommand(current_target, 'take images')
                    os.system(f'python3 {parentPath}/cameras/camera_control.py')
                    logger.info("Started the camera module.")

                    guideThread = threading.Thread(target=correctTracking, args=(mount_port, coordinates, ASTROMETRY_API, ABORT_FAILED_SOLVE_ATTEMPT), daemon=True)
                    guideThread.start()

            case 'park':
                print("Parking the mount.")
                logger.info("Parking the mount.")
                park(mount_port, UNIT_LOCATION)
                sendTargetObjectCommand(current_target, 'parked')
                time.sleep(2)
                mount_port.close()
                logger.debug("Closed the mount's serial port.")
                break
                
            case 'emergency park':
                print("Parking the mount and aborting observation of this target")
                park(mount_port, UNIT_LOCATION)
                sendTargetObjectCommand(current_target, 'emergency parked')

            case 'close mount serial port':
                mount_port.close()
                sendTargetObjectCommand(current_target, 'stopped mount serial')

            case 'observation complete':
                print(f"Done looking at {current_target.name}. Parking the mount.")
                logger.info(f"Done looking at {current_target.name}. Parking the mount.")
                park(mount_port, UNIT_LOCATION)
                sendTargetObjectCommand(current_target, 'parked')
                mount_port.close()
                logger.debug("Closed the mount's serial port.")
                break
            
            case _:
                continue

if __name__ == '__main__':
    logger = astroLogger(enable_color=True)
    main()
