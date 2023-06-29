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

            ###!!! things get funky, the mount doesn't have a go to serial command. instead, we have to start moving by a speed in directions and then stop moving in the specified directions !!!### 
            Coordinate_Difference = input - mount_response #!!!!! Wont work, need to setup a way of turning response commands into SkyCord objects

            ### Dimension is independently controlled (RA & DEC) have their own commands
            ### Sign is ALSO independently controlled, so we need logic to go from SkyCoord with (RA DEC) coordinates to the following serial commands:
            #  “:mn#”, “:me#”, “:ms#” or “:mw#”

            move_time = Coordinate_Difference / slew_rate_RA_DEC_tuple

            ### Start a timer, start slewing

            ### Once timer has gone off, stop moving

            ### Start tracking
        elif input == 'go_safe':

            # Call function used above ^ with RA DEC coordinates that face the ground
            mount_abstract_serial_port.write(b':MP1') # Parks the mount
        elif input == 'close_comms':
            mount_abstract_serial_port.close()
