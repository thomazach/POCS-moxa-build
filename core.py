#!/usr/bin/python3
from setuptools import setup, find_packages
import sys
import os
import heapq
import pickle
import math
import time
import threading

from yaml import safe_load
from datetime import datetime, timezone

from astropy import units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation, SkyCoord, AltAz, Angle, get_body

import subprocess
from observational_scheduler import obs_scheduler

WEATHER_RESULTS_TXT = 'weather_results.txt'
TARGETS_FILE_PATH = 'conf_files/test_fields.yaml'

yesOrNo = lambda x: x == 'y' or x == 'Y' or x == 'yes' or x == 'Yes'
BACKGROUND_FLAG = 0

class backgroundThread (threading.Thread):
    def __init__(self, threadName):
        threading.Thread.__init__(self)
        self.threadName = threadName

    def run(self):
        # put logger statement
        parentDirectory = os.getcwd()
        with open(f"{parentDirectory}/conf_files/settings.yaml", 'r') as f:
            settings = safe_load(f)

        TARGETS_FILE_PATH = f"{parentDirectory}/conf_files/targets/{settings['TARGET_FILE']}"
        LAT_CONFIG = settings['LATITUDE']
        LON_CONFIG = settings['LONGITUDE']
        ELEVATION_CONFIG = settings['ELEVATION']
        UNIT_LOCATION = EarthLocation(lat=LAT_CONFIG, lon=LON_CONFIG, height=ELEVATION_CONFIG * u.m)

        print(TARGETS_FILE_PATH, LAT_CONFIG, LON_CONFIG, ELEVATION_CONFIG)

        while True:

            _writeToFile(WEATHER_RESULTS_TXT, 'go')
            _writeToFile(WEATHER_RESULTS_TXT, 'true') # Temporarily need to bypass weather module until panoptes team figures out solution for weather sensor
            
            time.sleep(3)
            weather_results = readWeatherResults(WEATHER_RESULTS_TXT)
            isNight = astronomicalNight(UNIT_LOCATION)
            print(f"Astronomical night: {isNight} Weather Results: {weather_results}")
            if weather_results == 'true' and isNight == True:
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
            else:
                print('not safe')

                # Things aren't safe so the mount needs to be told to cry
                # break
            
            time.sleep(300)

class command:
    def __init__(self, userInput):
        try:
            parts = userInput.split()
        except Exception as error:
            print('=ERROR= ', error)

        if len(parts) == 1:
            cmd = parts[0]
            if cmd == 'start':
                if BACKGROUND_FLAG == 0:
                    thread = backgroundThread('background')
                    thread.start()
                    BACKGROUND_FLAG.__add__(1)
                    return
                elif BACKGROUND_FLAG >= 1:
                    print('background is already running')
                else:
                    print('An error has occured while trying to launch')
            realFile = None
            for file in os.listdir('./user_scripts'):
                if file.split('.')[0] == cmd:
                    realFile = file
            subprocess.run('./user_scripts/' + realFile)
        else:
            cmd = parts[0]
            args = parts[1:]
            realFile = None
            for file in os.listdir('./user_scripts'):
                if file.split('.')[0] == cmd:
                    realFile = file
            commandArray = ['./user_scripts/' + realFile]
            subprocess.Popen(commandArray + args, cwd=os.path.dirname(os.path.realpath(__file__)))

def _writeToFile(PATH, msg):
    file_write = open(PATH, "w")
    file_write.write(msg)
    file_write.close()

def _betterInput(prompt, Type = str, default = None):
    #TODO: Implement the mountCommand class so that I can also have it 
    #      handled here

    result = None
    while result == None:
        userInput = input(prompt) or default
        if userInput:
            try:
                result = Type(userInput)
            except TypeError as error:
                print('=INVALID= Your input was not of type ', Type)
                userInput = None
            except Exception as error:
                print('=ERROR= ', error)
                userInput = None
    return result

def makeObservationDict():

    #TODO: Handle bad inputs

    def _makeCameraArr():
        camera = {}
        camera['num_captures'] = None
        camera['exposure_time'] = None
        camera['take_images'] = yesOrNo(input('Do you want this camera to take images [y/n]: '))
        if camera['take_images']:
            camera['num_captures'] = _betterInput('Enter # of images to capture: ', Type=int, default=1)
            camera['exposure_time'] = _betterInput('Enter exposure time per image in seconds: ', Type=int, default=1)
        return camera

    note = _betterInput('Enter user note [leave blank if none]: ', default='None')
    priority = _betterInput('Input the priority of the observation as a positive whole number: ', Type=int, default=0)
    ra = _betterInput('Input the ra: ', default='00 42 44')
    dec = _betterInput('Input the dec: ', default='+41 16 09')
    cmd = _betterInput('Input the command [leave blank for slew]: ', default='slew to target')
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

    keepGoing = 1
    while keepGoing == 1:
        cmd = _betterInput("Command: ", command, None)


if __name__ == "__main__":
    main()