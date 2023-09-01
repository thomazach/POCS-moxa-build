import os
import sys
import heapq
import pickle
import math
import time
import threading

from yaml import safe_load
from datetime import datetime, timezone, timedelta

from astropy import units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation, SkyCoord, AltAz, Angle, get_body

# TODO: Add colors and see if its possible to force it to print below the command line

PARENT_DIRECTORY = os.path.dirname(__file__).replace('/core', '')
sys.path.append(PARENT_DIRECTORY)

WEATHER_RESULTS_TXT = f"{PARENT_DIRECTORY}/weather_results.txt"

from observational_scheduler import obs_scheduler
from user_scripts.schedule import bcolors

def _writeToFile(PATH, msg):
    file_write = open(PATH, "w")
    file_write.write(msg)
    file_write.close()

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

    print(bcolors.OKCYAN + "It isn't astronomical night yet." + bcolors.ENDC)
    return False

def aboveHorizon(targetSkyCoord, unitLocation):
    targetAltAz = convertRaDecToAltAZ(targetSkyCoord, unitLocation)
    
    if float(targetAltAz.alt.deg) < 0:
        print(bcolors.OKCYAN + "Target is below the horizon." + bcolors.ENDC)
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
        print(bcolors.OKCYAN + "Current target obstructed by moon." + bcolors.ENDC)
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

def POCSMainLoop(UNIT_LOCATION, TARGETS_FILE_PATH, settings):
    # The bread and butter of core. Responsible for sending commands to mount and
    # deciding what to observe. Its a function so that it can be threaded. This allows
    # the panoptes-CLI stop command to stop the observation process quickly without having
    # to wait for the condition check loop which is 5 minutes.
    
    global doRun

    while doRun:

        _writeToFile(WEATHER_RESULTS_TXT, 'go')
        _writeToFile(WEATHER_RESULTS_TXT, 'true') # Temporarily need to bypass weather module until panoptes team figures out solution for weather sensor
        
        time.sleep(3)
        weather_results = readWeatherResults(WEATHER_RESULTS_TXT)
        isNight = astronomicalNight(UNIT_LOCATION)

        if weather_results == 'true' and isNight == True:
            print(f"{bcolors.OKGREEN}Starting observation using schedule file: {bcolors.OKCYAN}{settings['TARGET_FILE']}{bcolors.ENDC}")
            target_queue = obs_scheduler.getTargetQueue(TARGETS_FILE_PATH)
            while target_queue != []:
                global target
                target = heapq.heappop(target_queue)
                print(f"{bcolors.OKCYAN}Checking observation conditions of the current target: {target.name}.{bcolors.ENDC}")
                if not checkTargetAvailability(target.position['ra'] + target.position['dec'], UNIT_LOCATION):
                    print(bcolors.OKCYAN + "Moving to next target in schedule file." + bcolors.ENDC)
                    continue
                # tell mount controller target
                with open(f"{PARENT_DIRECTORY}/pickle/current_target.pickle", "wb") as pickleFile:
                    pickle.dump(target, pickleFile)
                os.system(f'python3 {PARENT_DIRECTORY}/mount/mount_control.py')
                # wait for mount to say complete
                while doRun:
                    time.sleep(5)
                    with open(f"{PARENT_DIRECTORY}/pickle/current_target.pickle", "rb") as f:
                        target = pickle.load(f)
                    
                    # TODO: Add safety feature for weather checking & astronomical night checking
                    # TODO: Add safety feature that sends the mount the emergency park command if this loop has ran 10+ min longer than expected observation time (could also send raw serial)

                    if target.cmd == 'observation complete':
                        print(bcolors.OKGREEN + f"Observation of {target.name} complete!" + bcolors.ENDC)
                        break

                # get data from camera
                # ask storage if full 
                #   if full handle or notify somehow
                #   else upload or store picture in storage method

            # when it is safe to go we need to send 
            _writeToFile(WEATHER_RESULTS_TXT, 'exit')
        else:
            print(bcolors.OKCYAN + "Observation conditions not met. Trying again in 5 minutes." + bcolors.ENDC)

            # Things aren't safe so the mount needs to be told to cry
            # break
        
        nextConditionCheck = datetime.now() + timedelta(minutes=5)
        while doRun:
            if nextConditionCheck <= datetime.now():
                break
            time.sleep(1)
            

doRun = True
target = None
def main():
    print(bcolors.PURPLE + "\nSystem is now in automated observation state." + bcolors.ENDC)
    # put logger statement
    with open(f"{PARENT_DIRECTORY}/conf_files/settings.yaml", 'r') as f:
        settings = safe_load(f)

    TARGETS_FILE_PATH = f"{PARENT_DIRECTORY}/conf_files/targets/{settings['TARGET_FILE']}"
    LAT_CONFIG = settings['LATITUDE']
    LON_CONFIG = settings['LONGITUDE']
    ELEVATION_CONFIG = settings['ELEVATION']
    UNIT_LOCATION = EarthLocation(lat=LAT_CONFIG, lon=LON_CONFIG, height=ELEVATION_CONFIG * u.m)

    while True:
        # Graceful on off switch
        with open(f"{PARENT_DIRECTORY}/pickle/system_info.pickle", "rb") as f:
            systemInfo = pickle.load(f)
        
        if systemInfo['desired_state'] == 'on' and systemInfo['state'] == 'off':
            loop = threading.Thread(target=POCSMainLoop, args=[UNIT_LOCATION, TARGETS_FILE_PATH, settings]).start()
            systemInfo['state'] = 'on'
            with open(f"{PARENT_DIRECTORY}/pickle/system_info.pickle", "wb") as f:
                pickle.dump(systemInfo, f)

        if systemInfo['desired_state'] == 'off' and systemInfo['state'] == 'on':
            global doRun
            global target

            doRun = False

            if (target is not None) and (target.cmd != 'observation complete'):
                target.cmd = 'park'
                with open(f"{PARENT_DIRECTORY}/pickle/current_target.pickle", "wb") as pickleFile:
                        print(target.cmd)
                        pickle.dump(target, pickleFile)
                
            systemInfo['state'] = 'off'
            break

        time.sleep(5)

    with open(f"{PARENT_DIRECTORY}/pickle/system_info.pickle", "wb") as f:
                pickle.dump(systemInfo, f)
    
    print(bcolors.PURPLE + "\nExited automated observation state. Resting." + bcolors.ENDC)

if __name__ == '__main__':
    main()