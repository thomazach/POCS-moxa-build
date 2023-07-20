import time
import serial
import yaml
from astropy import units as u
from astropy.coordinates import SkyCoord


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

### Recieve a command from moxa-pocs/core, since this is being written before moxa-pocs/core, i will be using a dummy function that manually feeds input
def get_mount_command(dtype='SkyCoord'):

    if dtype == 'SkyCoord':
        return SkyCoord('00 42 44 +41 16 09', unit=(u.hourangle, u.deg))
    elif dtype == 'close_comms':
        return 'close_comms'
    else:
        return 'go_safe'
    
### Testing function, should use 
def get_mount_port():
    return '/dev/ttyUSB0'

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
    DEV NOTES: 
        -Replace test prints with serial writes + logging functionality
        -Blocks for a long period of time, consider moving to seperate thread.

    Takes the RA and DEC tuples from create_movement_commands function and executes them using serial
    communication. For testing purposes, only supports print statements currently (7/5/2023).

    Does not execute commands concurrently.

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

        print(f"Sending serial command: ':ST1#' to start tracking SkyCoord: {get_mount_command()}")
        mount_serial_port.write(b':ST1#')

    # Ready to take pictures. Call camera_control.py and send camera data if necessary.

def connect_to_mount():
    '''
    Make sure mount is working and get important starting information:
    
    1. Use ':MountInfo#' to confirm serial communication 
    2. Get and return current RA and DEC coordinates
    3. Check the tracking rate is set to 256x sidereal and change it if it is wrong
    '''

    # Open serial communication
    with serial.Serial(get_mount_port(), 9600, timeout=1) as mountSerialPort:
        
        # Verify that the mount is communicating as expected
        mountSerialPort.write(b':MountInfo#')
        modelNumber = mountSerialPort.read(4)
        if modelNumber != b'0030':
            raise Exception("Incorrect model number: Bad serial communication. Required mount for this software is the iEQ30Pro from iOptron.")
        
        # Get the current RA and DEC coordinates
        mountSerialPort.write(b':GEC#')
        currentCoordinates = mountSerialPort.read(21) # Expected reponse format is: “sTTTTTTTTXXXXXXXX#”
        # Split this into an (RA, DEC) tuple and decode the DEC XXXXX part which doesn't have a sign. Test on hardware first.

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

mount_port, START_COORDINATES = connect_to_mount()

if START_COORDINATES != None: # Caveman intelect data check, improve later

    ### Start main mount loop that listens for incoming command from moxa-pocs/core and executes as necessary
    while True:

        input = get_mount_command()

        ### Check that input is the right data type, DO NOT UNPARK OR MOVE IF NOT
        if isinstance(input, SkyCoord): # Refine later

            ########### Make this entire section into a callable function #####################

            mount_port.write(b':MP0#') # Unpark mount, dont need to check if its already unparked, as command has no effect if already unparked

            RA_tuple, DEC_tuple = create_movement_commands(START_COORDINATES, get_mount_command(dtype='SkyCoord'))

            execute_movement_commands(mount_port, RA_tuple, DEC_tuple)
        elif input == 'go_safe':
            # Park the mount
            print("Parking the mount!")
            mount_port.write(b':MP1#')
        elif input == 'close_comms':
            mount_port.close()
        elif input == 'listen':
            # Set the listen command to None in whatever communication method we choose
            continue
        else:
            # Park the mount if communication with core/obs scheduler is lost
            # When setting up communication between mount_controller and core/obs scheduler there needs to be a heart beat, 
            # so that 
            print("Parking the mount!")
            mount_port.write(b':MP1#')
