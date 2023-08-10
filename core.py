import os
import heapq
import pickle
import random
import math

import time
from datetime import datetime, timezone

from astropy import units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation, SkyCoord, AltAz, Angle, get_body

from observational_scheduler import obs_scheduler

WEATHER_RESULTS_TXT = 'weather_results.txt'
TARGETS_FILE_PATH = 'conf_files/test_fields.yaml'
LAT_CONFIG = '44.56725'
LON_CONFIG = '-123.28925'
ELEVATION_CONFIG = 71.628
UNIT_LOCATION = EarthLocation(lat=LAT_CONFIG, lon=LON_CONFIG, height=ELEVATION_CONFIG * u.m)

random.seed(time.time_ns)

yesOrNo = lambda x: x == 'y' or x == 'Y' or x == 'yes' or x == 'Yes'

def _writeToFile(PATH, msg):
    file_write = open(PATH, "w")
    file_write.write(msg)
    file_write.close()

def makeObservationDict():

    #TODO: Handle bad inputs

    def _makeCameraArr():
        camera = {}
        camera['num_captures'] = None
        camera['exposure_time'] = None
        camera['take_images'] = yesOrNo(input('Do you want this camera to take images [y/n]: '))
        if camera['take_images']:
            camera['num_captures'] = int(input('Enter # of images to capture: ') or 1)
            camera['exposure_time'] = int(input('Enter exposure time per image in seconds: ') or 1)
        return camera

    note = str(input('Enter user note [leave blank if none]: ') or None)
    priority = int(input('Input the priority of the observation \nas a positive whole number: ') or 0)
    ra = str(input('Input the ra: ') or '00 42 44')
    dec = str(input('Input the dec: ') or '+41 16 09')
    cmd = str(input('Input the command [leave blank for slew]: ') or 'slew to target')
    print('Primary Camera Settings: \n')
    primaryCam = _makeCameraArr()
    print('Secondary Camera Settings: \n')
    secondaryCam = _makeCameraArr()
    attributes = {}
    attributes['user_note'] = note
    attributes['priority'] = priority
    attributes['ra'] = ra
    attributes['dec'] = dec
    attributes['cmd'] = cmd
    attributes['primary_cam'] = primaryCam
    attributes['secondary_cam'] = secondaryCam
    return attributes


def readWeatherResults(PATH):
    weather_results_file_object = open(PATH, 'r')
    weather_results = weather_results_file_object.readline()
    weather_results_file_object.close()
    return weather_results

def convertRaDecToAltAZ(skyCoord, location):
    observationTime = Time(datetime.now(timezone.utc))
    localFrame = AltAz(location=location, obstime=observationTime)

    return skyCoord.transform_to(localFrame)

def astronomicalNight(unitLocation):
    sun = get_body('sun', Time(datetime.now(timezone.utc)))
    sunAltAz = convertRaDecToAltAZ(sun, unitLocation)

    if float(sunAltAz.alt.deg) < -18:
        return True

    print("It isn't astronomical night yet.")
    return False

def aboveHorizon(targetSkyCoord, unitLocation):
    targetAltAz = convertRaDecToAltAZ(targetSkyCoord, unitLocation)
    
    if float(targetAltAz.alt.deg) < 0:
        print("Target is below the horizon.")
        return False
    return True

    
def moonObstruction(targetSkyCoord):
    current_time = Time(datetime.now(timezone.utc))
    moon = get_body('moon', current_time)

    # Need to calculate lunar phase percentage to determine level of avoidance
    ### Adapted from astroplan: https://github.com/astropy/astroplan/blob/main/astroplan/moon.py (8/3/2023)
    sun = get_body('sun', current_time)
    seperation = float(sun.separation(moon).rad)
    sunDistance = float(sun.distance.au)
    lunar_orbital_phase_rad = math.atan2(sunDistance * math.sin(seperation), float(moon.distance.au) - sunDistance * math.cos(seperation))
    percent_illuminated = (1 + math.cos(lunar_orbital_phase_rad))/2

    # Never try to look at something through the moon, and look further away from the moon the brighter it is
    moonRadius = Angle("34.1'") / 2
    moonAvoidanceRadius = moonRadius + percent_illuminated * Angle(60, u.deg)
    target_ra, target_dec = (float(targetSkyCoord.ra.rad), float(targetSkyCoord.dec.rad))
    moon_ra, moon_dec = (float(moon.ra.rad), float(moon.dec.rad))
    # Angular distance between two points on a sphere
    angular_diff = math.acos(math.sin(moon_dec) * math.sin(target_dec) + math.cos(moon_dec) * math.cos(target_dec) * math.cos(target_ra - moon_ra))

    if angular_diff < moonAvoidanceRadius.rad:
        print("Current target obstructed by moon.")
        return False
    
    return True

def checkTargetAvailability(position, unitLocation):
    checkFunctions = [(astronomicalNight, [unitLocation]),
                    (aboveHorizon, [SkyCoord(position, unit=(u.hourangle, u.deg)), unitLocation]),
                    (moonObstruction, [SkyCoord(position, unit=(u.hourangle, u.deg))])
    ]

    for func, args in checkFunctions:
        if not func(*args):
            return False
    return True

def main():

    keepGettingObservations = True
    observationsDict = {}
    while keepGettingObservations:
        name = str(input('Name of the observation: '))
        attributes = makeObservationDict()
        observationsDict[name] = attributes
        keepGettingObservations = yesOrNo(input('Add another observation [y/n]: '))
    obs_scheduler.createObservationList(observationsDict)

    _writeToFile(WEATHER_RESULTS_TXT, 'go')
    _writeToFile(WEATHER_RESULTS_TXT, 'true') # Temporarily need to bypass weather module until panoptes team figures out solution for weather sensor
    while True: 
        
        time.sleep(3)
        weather_results = readWeatherResults(WEATHER_RESULTS_TXT)
        print(weather_results)
        if weather_results == 'true':
            print('Safe to use')
            target_queue = obs_scheduler.getTargetQueue(TARGETS_FILE_PATH)
            while target_queue != []:
                target = heapq.heappop(target_queue)
                if not checkTargetAvailability(target.position['ra'] + target.position['dec'], UNIT_LOCATION):
                    continue
                # tell mount controller target
                with open("pickle/current_target.pickle", "wb") as pickleFile:
                    pickle.dump(target, pickleFile)
                os.system('python mount/mount_control.py')
                # wait for mount to say complete
                while True:
                    time.sleep(30)
                    with open("pickle.current_target.pickle", "rb") as f:
                        target = pickle.load(f)
                    
                    # TODO: Add safety feature that sends the mount the emergency park command if this loop has ran 10+ min longer than expected observation time (could also send raw serial)

                    if target.cmd == 'observation complete':
                        break

                # get data from camera
                # ask storage if full 
                #   if full handle or notify somehow
                #   else upload or store picture in storage method

            # when it is safe to go we need to send 
            _writeToFile(WEATHER_RESULTS_TXT, 'exit')
            break
        else:
            print('not safe')

            # Things aren't safe so the mount needs to be told to cry
            # break

if __name__ == "__main__":
    main()