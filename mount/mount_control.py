import time
import serial
from astropy import units as u
from astropy.coordinates import SkyCoord


'''

First attempt at mount control. This section(directory: moxa-pocs/mount) needs to handle the following inputs from moxa-pocs/core:

1. an astropy.coordinates.SkyCoord object
    -unpark the mount if necessary
    -move to the target
    -start tracking it
2. go to the safe position and park
    -point the cameras at the ground 
    -park the mount
3. handle mount drift corrections (yikes, putting that on the backburner. might not be necessariy with wide FOV cameras)


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
        dec_cmd = ':mn#'
    elif dec_diff > 0:
        dec_cmd = ':ms#'
    else:
        dec_cmd = ''

    if ra_diff < 0:
        ra_cmd = ':me#'
    elif ra_diff > 0:
        ra_cmd = ':mw#'
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

    ra_start_time = time.time()
    print(f"Sent serial command: {ra_cmd} Execution time: {ra_time}")
    while (ra_start_time + ra_time + 5) > time.time():
        
        if ra_start_time + ra_time <= time.time():
            print(f"Sent serial command ':qR#' to stop RA mount movement at {time.time()}")
            print(f"Actual execution time is {time.time() - ra_start_time}")
            break

    dec_start_time = time.time()
    print(f"Sent serial command: {dec_cmd} Execution time: {dec_time}")
    while (dec_start_time + dec_time + 5) > time.time():

        if dec_start_time + dec_time <= time.time():
            print(f"Sent serial command ':qD#' to stop DEC mount movement at {time.time()}")
            print(f"Actual execution time is {time.time() - dec_start_time}")
            break

    print(f"Sent serial command: ':ST1#' to start tracking SkyCoord: {get_mount_command()}")
### Open serial communication on the mounts serial port
mount_abstract_serial_port = serial.Serial(get_mount_port(), 9600) # Maybe get 9600 from a config file? doubt they use different serail for same cmd langague
### Make sure mount is working and get important starting information
mount_abstract_serial_port.write(b':GEP#') #':GEP#' gets right acension and declination, can use this to confirm the mount is communicating properly
mount_abstract_serial_port.timeout = 10 # Set timeout of serial object to 10 seconds before waiting for the response
mount_response = mount_abstract_serial_port.read(21) # Read 21 bytes since the expected reponse is formatted as: “sTTTTTTTTTTTTTTTTTnn#”
mount_abstract_serial_port.write(b':<get RA DEC movement rates>#') #':GTR#' ?? maybe google telescope stuff
slew_rate_RA_DEC_tuple = mount_abstract_serial_port.read(-1) # Don't know int value

if mount_response != None: # Caveman intelect data check, improve later

    ### Start main mount loop that listens for incoming command from moxa-pocs/core and executes as necessary
    while True:

        input = get_mount_command()

        ### Check that input is the right data type, DO NOT UNPARK OR MOVE IF NOT
        if isinstance(input, SkyCoord): # Refine late

            ########### Make this entire section into a callable function #####################

            mount_abstract_serial_port.write(b':MP0#') # Unpark mount, dont need to check if its already unparked, as command has no effect if already unparked

            RA_tuple, DEC_tuple = create_movement_commands(mount_response, get_mount_command(dtype='SkyCoord'))

            execute_movement_commands('dev/TEStty0', RA_tuple, DEC_tuple)
        elif input == 'go_safe':

            #! Still need to call function used above ^ with RA DEC coordinates that face the ground

            mount_abstract_serial_port.write(b':MP1') # Parks the mount
        elif input == 'close_comms':
            mount_abstract_serial_port.close()
