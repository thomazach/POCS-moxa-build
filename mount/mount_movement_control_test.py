import time

from astropy.coordinates import SkyCoord
from astropy import units as u

'''
Preliminary testing to outline how a sky coord can be changed from a
RA DEC coordinate into a series of serial commands for the mount. Is a procedural
version of mount_control.py without safety checks or variable input or dummy functions feeding
input expected from pocs.core.

Demonstrates hopefully functional mount motion, without serial communication. It is theoretically complete, with movement times
accurate to +- 0.01 
'''

current_pos = SkyCoord('00 00 00 +00 00 00', unit=(u.hourangle, u.deg))
pos = SkyCoord('00 42 44 +41 16 09', unit=(u.hourangle, u.deg))

# Find RA and DEC difference
dec_diff = pos.dec.degree - current_pos.dec.degree
ra_diff = pos.ra.degree - current_pos.ra.degree

# Logic
if dec_diff < 0: # if dec_diff is negative
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

# Make sure sidereal time is correct for normal tracking:
# serial.write(b':RT0#')
# Set the slewing rate to be  sidereal * 256:
# serial.write(b':MSR7#) // Response = 1

# sidereal rate = 15.042 arcseconds / seconds
# 3600 arcseconds = 1 degree
# 1 degree / 3600 arcseconds * 15.042 arcseconds/ seconds
# = 15.042 / 3600 degrees / second 
# 3600 / 15.042 seconds / degree

dec_time = 1 / (15.042 / 3600 * 256) * dec_diff
ra_time = 1/ (15.042 / 3600 * 256) * ra_diff

dec_move_tuple = (dec_cmd, dec_time)
ra_move_tuple = (ra_cmd, ra_time)

print(ra_move_tuple)
print(dec_move_tuple)


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

print(f"Sent serial command: ':ST1#' to start tracking SkyCoord: {pos}")
