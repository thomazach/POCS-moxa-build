# NOT FULLY HARDWARE TESTED
import os
import sys
import time
import serial
import pickle
from astropy import units as u
from astropy.coordinates import SkyCoord

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from observational_scheduler.obs_scheduler import target

'''

First attempt at mount control. This section(directory: moxa-pocs/mount) needs to handle the following inputs from moxa-pocs/core:

1. an astropy.coordinates.SkyCoord object
    -unpark the mount if necessary
    -move to the target
    -start tracking it
2. Call camera_control with the proper information.
3. go to the safe position and park
    -point the cameras at the ground 
    -park the mount
4. handle mount drift corrections (yikes, putting that on the backburner. might not be necessariy with wide FOV cameras)


Commands are sent using iOptron Mount RS-232 Command Langauge. The jist is that you send a string of the form ':<command characters>#', 
and then the mount will respond over serial with a formatted response, which depends on the command that was sent. This will be done using pySerial.

'''
### Testing function, should use auto detection in the future 
def get_mount_port():
    return '/dev/ttyUSB0'

def connect_to_mount():

    # Open serial communication with the mount
    with serial.Serial(get_mount_port(), 9600, timeout=1) as mountSerialPort:
        
        # Verify that the mount is communicating as expected
        mountSerialPort.write(b':MountInfo#')
        modelNumber = mountSerialPort.read(4)
        if modelNumber != b'0030':
            raise Exception("Incorrect model number: Bad serial communication. Required mount for this software is the iEQ30Pro from iOptron.")
        
        ### NEED TO TEST THIS COMMAND ITS UNCLEAR WHICH SETTING EFFECTS THE SLEWING SPEED ###
        # Set the mount to slew at 256x sidereal using "N S E W buttons"
        mountSerialPort.write(b':SR7#') 
        
        # Get the current RA and DEC coordinates
        mountSerialPort.write(b':GEC#')
        currentCoordinates = mountSerialPort.read(21) # Expected reponse format is: “sTTTTTTTTXXXXXXXX#”
        # Need to split this into an (RA, DEC) tuple and decode the DEC XXXXX part which doesn't have a sign. Test on hardware first.

        # Check that the slewing rate is its slowest value for max accuracy, and set it if it isn't
        mountSerialPort.write(b':GSR#')
        slewingSpeed = mountSerialPort.read(2)
        if slewingSpeed != b'7#':
            print("Incorrect slewing rate, attempting to set it to 256x sidereal")
            mountSerialPort.write(b':MSR7#')
            if mountSerialPort.read(1) == b'1':
                print("Succesfully updated slewing rate.")
            else:
                raise Exception("Problem setting sidereal tracking rate to 256x sidereal")
        
        return mountSerialPort, currentCoordinates
    
### Recieve a command from moxa-pocs/core by loading the pickle instance it has provided in the pickle directory
def request_mount_command():
    relative_path = os.path.dirname(__file__).replace('mount', 'pickle')
    with open(f"{relative_path}\current_target.pickle", "rb") as f:
        current_target = pickle.load(f)

    return current_target

def sendTargetObjectCommand(current_target_object, cmd):
    current_target_object.cmd = cmd
    with open("pickle/current_target.pickle", "wb") as f:
        pickle.dump(current_target_object, f)

def create_movement_commands(current_position, desired_position):
    '''
    This function takes in the mounts current position and the position which the caller
    wants to go to. This is called the desired position.

    WILL ONLY WORK USING STANDARD SIDEREAL TIME:
    Make sure sidereal time is correct for normal tracking:

    serial.write(b':RT0#')
    serial.write(b':MSR7#)

    The above serial commands make it so that the sidereal RA rate is that required to track
    stars and sets the mounts slewing rate to target to be 256 times the speed of the sidereal
    rate respectively. 


    Inputs:
        Both inputs are astropy.coordinate SkyCoord objects with defined units.
    
    Output:
        A tuple of two tuples: return ra_tuple, dec_tuple
        Each axis tuple is of the form:
        (movement_direction, time_to_spend_moving)
            movement_direction:
            A string corresponding to one of the mount's serial commands to move in +-RA/DEC
            time_to_spend_moving:
            A float representing the amount of time to move along the specified axis in SECONDS

    '''
    # Find RA and DEC difference
    dec_diff = desired_position.dec.degree - current_position.dec.degree
    ra_diff = desired_position.ra.degree - current_position.ra.degree

    # Give each axis the right command based on the difference in axis degrees
    if dec_diff < 0:
        dec_cmd = b':mn#'
    elif dec_diff > 0:
        dec_cmd = b':ms#'
    else:
        dec_cmd = ''

    if ra_diff < 0:
        ra_cmd = b':me#'
    elif ra_diff > 0:
        ra_cmd = b':mw#'
    else:
        ra_cmd = ''


    # sidereal rate = 15.042 arcseconds / seconds
    # 3600 arcseconds = 1 degree
    # 1 degree / 3600 arcseconds * 15.042 arcseconds/ seconds
    # = 15.042 / 3600 degrees / second 
    # 3600 / 15.042 seconds / degree

    dec_time = 3600 / 15.042 * 256 * dec_diff
    ra_time = 3600 / 15.042 * 256 * ra_diff

    dec_tuple = (dec_cmd, dec_time)
    ra_tuple = (ra_cmd, ra_time)

    return ra_tuple, dec_tuple

def execute_movement_commands(mount_serial_port, RA_tuple, DEC_tuple):
    '''
    Takes the RA and DEC tuples from create_movement_commands function and executes them using serial
    communication.

    Does not execute motion of the ra and dec axis at the same time.
    '''

    ra_cmd, ra_time = RA_tuple
    dec_cmd, dec_time = DEC_tuple

    dec_start_time = time.time()
    with mount_serial_port:
        print(f"Sending serial command: {dec_cmd} with desired execution time of {dec_time} seconds")
        mount_serial_port.write(dec_cmd)
        while (dec_start_time + dec_time + 5) > time.time():

            if dec_start_time + dec_time <= time.time():
                print(f"Sending serial command ':qD#' to stop DEC mount movement at {time.time()}")
                mount_serial_port.write(b':qD#')
                print(f"Actual execution time is {time.time() - dec_start_time}")
                break

        ra_start_time = time.time()
        print(f"Sending serial command: {ra_cmd} with desired execution time of {ra_time} seconds")
        mount_serial_port.write(ra_cmd)
        while (ra_start_time + ra_time + 5) > time.time():
            
            if ra_start_time + ra_time <= time.time():
                print(f"Sent serial command ':qR#' to stop RA mount movement at {time.time()}")
                mount_serial_port.write(b':qR#')
                print(f"Actual execution time is {time.time() - ra_start_time}")
                break

        print(f"Sending serial command: ':ST1#' to start tracking...")
        mount_serial_port.write(b':ST1#')

def main():
    mount_port, START_COORDINATES = connect_to_mount()

    if START_COORDINATES != None: # Caveman intelect data check, improve later

        ### Start main mount loop that listens for incoming command from moxa-pocs/core and executes as necessary
        while True:
        
            time.sleep(1)

            current_target = request_mount_command()

            match current_target.cmd:

                case 'slew to target':
                    mount_port.write(b':MP0#') # Unpark mount, dont need to check if its already unparked since command has no effect if already unparked
                    RA_tuple, DEC_tuple = create_movement_commands(START_COORDINATES, SkyCoord(current_target.position['ra'], current_target.position['dec'], unit=(u.hourangle, u.deg)))
                    execute_movement_commands(mount_port, RA_tuple, DEC_tuple)
                    sendTargetObjectCommand(current_target, 'take images')
                    os.system('cd .. ; python cameras/camera_control.py')

                case 'park':
                    print("Parking the mount.")
                    mount_port.write(b':MP1#')
                    sendTargetObjectCommand(current_target, 'parked')
                    
                case 'emergency park':
                    print("Parking the mount and aborting observation of this target")
                    mount_port.write(b':MP1#')
                    sendTargetObjectCommand(current_target, 'emergency parked')

                case 'close mount serial port':
                    mount_port.close()
                    sendTargetObjectCommand(current_target, 'stopped mount serial')

                case 'observation complete':
                    print("Observation complete. Parking the mount.")
                    mount_port.write(b':MP1#')
                    break
                
                case _:
                    continue

if __name__ == '__main__':
    main()
