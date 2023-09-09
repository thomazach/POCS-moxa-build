import os
import sys
import time
import serial
import pickle

from yaml import safe_load

from datetime import datetime, timezone

from astropy import units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation, SkyCoord, AltAz, Angle

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from observational_scheduler.obs_scheduler import target

parentPath = os.path.dirname(__file__).replace('/mount', '')


def request_mount_command():
    ### Recieve a command from moxa-pocs/core by loading the pickle instance it has provided in the pickle directory
    with open(f"{parentPath}/pickle/current_target.pickle", "rb") as f:
        current_target = pickle.load(f)

    return current_target

def sendTargetObjectCommand(current_target_object, cmd):
    ### Send a command to other modules via current_target.pickle
    current_target_object.cmd = cmd
    with open(f"{parentPath}/pickle/current_target.pickle", "wb") as f:
        pickle.dump(current_target_object, f)

def convertAltAztoRaDec(location, az, alt):
    # Az/Alt - astropy input strings in degrees (ex. "90d")
    observationTime = Time(datetime.now(timezone.utc))
    ParkPosLocal = AltAz(az=Angle(az), alt=Angle(alt), location=location, obstime=observationTime)

    return SkyCoord(ParkPosLocal).transform_to('icrs')

def get_mount_port():

    usbList = os.popen('ls /dev/ttyUSB*').read()
    usbList = usbList.split('\n')
    usbList.remove('')

    for usbPort in usbList:
        print(usbPort)
        with serial.Serial(usbPort, 9600, timeout=10) as mount:
            mount.write(b':MountInfo#')
            out = mount.read(4)
            print(out)
            if out == b'0030':
                return mount
    
    raise Exception("Failed to find mount. Possibly bad serial communication. Required mount for this software is the iEQ30Pro from iOptron.")

def connect_to_mount():

    mountSerialPort = get_mount_port()
    if not mountSerialPort.is_open:
                mountSerialPort.open()
    
    # Set the mount to slew at max speed, which is 1440 x Sidereal
    mountSerialPort.write(b':SR9#')
    out = mountSerialPort.read(1)
    # TODO: Add log message for out serial

    # Check that the slewing rate is its slowest value for max accuracy, and set it if it isn't
    mountSerialPort.write(b':GSR#')
    slewingSpeed = mountSerialPort.read(2)
    if slewingSpeed != b'9#':
        print("Incorrect slewing rate, attempting to set it to 1440x sidereal")
        mountSerialPort.write(b':MSR9#')
        if mountSerialPort.read(1) == b'1':
            print("Succesfully updated slewing rate.")
        else:
            raise Exception("Problem setting sidereal tracking rate to 1440x sidereal")
        
    return mountSerialPort

def getCurrentSkyCoord(port):
    ### Returns a SkyCoord object of whatever the mount thinks it's currently pointing at (polar alignment required) ###
    port.write(b':GEC#')
    rawPosition = port.read(18).decode('utf-8')
    rawDEC, rawRA = float(rawPosition[0:9]), float(rawPosition[9:17]) #(0.01 arcseconds, milliseconds)
    RADecimalDegree = rawRA * 1/1000 * 360/86400 # sec/millisec * deg/sec
    DECDecimalDegree = Angle(str(rawDEC * 1/100) + 's').deg
    
    return SkyCoord(RADecimalDegree, DECDecimalDegree, unit=u.deg)

def park_slewToTarget(coordinates, mountSerialPort):

    if not mountSerialPort.is_open:
        mountSerialPort.open()
    mountSerialPort.write(b':MH#')
    _ = mountSerialPort.read()

    time.sleep(20)

    if not mountSerialPort.is_open:
        mountSerialPort.open()
    mountSerialPort.write(b':SZP#')
    _ = mountSerialPort.read()

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
    print(f"Sending serial command: {ra_cmd}. Slewing RA axis with desired execution time of {ra_time} seconds")
    mountSerialPort.write(ra_cmd)
    while (ra_start_time + ra_time + 5) > time.time():
        
        if ra_start_time + ra_time <= time.time():
            mountSerialPort.write(b':qR#')
            _ = mountSerialPort.read()
            print(f"Sent serial command ':qR#'. Stoped slewing RA axis with an execution time of {time.time() - ra_start_time} seconds")
            break
    mountSerialPort.write(b':ST1#')
    _ = mountSerialPort.read()
    print("Tracking started on RA axis.")

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
        print(f"Sending serial command: {dec_cmd}. Slewing DEC axis with desired execution time of {dec_time} seconds")
        mountSerialPort.write(dec_cmd)
        while (dec_start_time + dec_time + 5) > time.time():

            if dec_start_time + dec_time <= time.time():
                mountSerialPort.write(b':qD#')
                _ = mountSerialPort.read()
                print(f"Sent serial command ':qD#'. Stopped DEC slewing with an execution time of {time.time() - dec_start_time} seconds")
                break

def slewToTarget(coordinates, mountSerialPort=None):

    if not mountSerialPort.is_open:
         mountSerialPort.open()
    mountSerialPort.write(b':MP0#')
    _ = mountSerialPort.read()
    mountSerialPort.write(b':MH#')
    _ = mountSerialPort.read()

    time.sleep(20)

    RA_string = str(round(coordinates.ra.deg * 24/360 * 60 * 60 * 1000))
    print(RA_string)
    print(len(RA_string))
    NumZeros = max(0, 8 - len(RA_string))
    print(f"{NumZeros=}")

    RA_milliseconds = "0" * NumZeros + RA_string
    print(RA_milliseconds)

    val = round(coordinates.dec.deg * 60 * 60 * 100)
    NumZeros = max(0, 8 - len(RA_string))
    if val >= 0:
        DEC_SignedCentiArcseconds = "+" + "0" * NumZeros + str(val)
    else:
        DEC_SignedCentiArcseconds = "-" + "0" * NumZeros + str(val)

    print(DEC_SignedCentiArcseconds)

    RA_cmd = f':Sr{RA_milliseconds}#'.encode()
    DEC_cmd = f':Sd{DEC_SignedCentiArcseconds}#'.encode()

    print(f"{RA_cmd=}      {DEC_cmd=}")

    if not mountSerialPort.is_open:
         mountSerialPort.open()
    mountSerialPort.write(RA_cmd)
    _ = mountSerialPort.read()
    print(_)
    mountSerialPort.write(DEC_cmd)
    _ = mountSerialPort.read()
    print(_)
    mountSerialPort.write(b':MS#')
    _ = mountSerialPort.read()
    print(_)
    time.sleep(30)

def park(mountSerialPort, location):

    parkPosition = convertAltAztoRaDec(location, "90d", "-90d")

    if not mountSerialPort.is_open:
        mountSerialPort.open()

    park_slewToTarget(parkPosition, mountSerialPort)

def main():

    PARENT_DIRECTORY = os.path.dirname(__file__).replace('/mount', '')

    with open(f"{PARENT_DIRECTORY}/conf_files/settings.yaml", 'r') as f:
        settings = safe_load(f)

    LAT_CONFIG = settings['LATITUDE']
    LON_CONFIG = settings['LONGITUDE']
    ELEVATION_CONFIG = settings['ELEVATION']
    UNIT_LOCATION = EarthLocation(lat=LAT_CONFIG, lon=LON_CONFIG, height=ELEVATION_CONFIG * u.m)

    mount_port = connect_to_mount()

    ### Start main mount loop that listens for incoming command from moxa-pocs/core and executes as necessary
    while True:
    
        time.sleep(1)

        current_target = request_mount_command()

        if not mount_port.is_open:
            mount_port.open()

        match current_target.cmd:

            case 'slew to target':
                print("System attempting to slew to target...")
                mount_port.write(b':MP0#') # command has no effect if already unparked
                _ = mount_port.read()
                slewToTarget(SkyCoord(current_target.position['ra'], current_target.position['dec'], unit=(u.hourangle, u.deg)), mount_port)
                sendTargetObjectCommand(current_target, 'take images')
                os.system(f'python {parentPath}/cameras/camera_control.py')

            case 'park':
                print("Parking the mount.")
                park(mount_port, UNIT_LOCATION)
                sendTargetObjectCommand(current_target, 'parked')
                time.sleep(2)
                mount_port.close()
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
                park(mount_port, UNIT_LOCATION)
                sendTargetObjectCommand(current_target, 'parked')
                mount_port.close()
                break
            
            case _:
                continue

if __name__ == '__main__':
    main()
