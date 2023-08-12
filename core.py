#!/usr/bin/python3
from setuptools import setup, find_packages
import sys
import os
import threading
import heapq
import time
import pickle
import subprocess
from observational_scheduler import obs_scheduler

WEATHER_RESULTS_TXT = 'weather_results.txt'
TARGETS_FILE_PATH = 'conf_files/test_fields.yaml'

yesOrNo = lambda x: x == 'y' or x == 'Y' or x == 'yes' or x == 'Yes'

class command:
    def __init__(self, userInput):
        try:
            parts = userInput.split()
        except Exception as error:
            print('=ERROR= ', error)

        if len(parts) == 1:
            cmd = parts[0]
            realFile = None
            for file in os.listdir('./user_scripts'):
                if file.split('.')[0] == cmd:
                    realFile = file
            subprocess.run('./user_scripts/' + realFile)
        elif parts[0] == '&':
            print('background process not in yet')
        else:
            cmd = parts[0]
            args = parts[1:]
            realFile = None
            for file in os.listdir('./user_scripts'):
                if file.split('.')[0] == cmd:
                    realFile = file
            commandArray = ['./user_scripts/' + realFile]
            subprocess.Popen(commandArray + args, cwd=os.path.dirname(os.path.realpath(__file__)))
            print('annoying')

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
    attributes['note'] = note
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

def checkTargetAvailability(target):
    # Moon avoidance
    return True

def main():

    test1 = _betterInput("Command: ", command, None)
    print('Mtest1: ', test1, ' \nMtype(test1): ', str(type(test1)))

    # keepGettingObservations = True
    # observationsDict = {}
    # while keepGettingObservations:
    #     name = str(input('Name of the observation: '))
    #     attributes = makeObservationDict()
    #     observationsDict[name] = attributes
    #     keepGettingObservations = yesOrNo(input('Add another observation [y/n]: '))
    # obs_scheduler.createObservationList(observationsDict)

    # _writeToFile(WEATHER_RESULTS_TXT, 'go')
    # _writeToFile(WEATHER_RESULTS_TXT, 'true') # Temporarily need to bypass weather module until panoptes team figures out solution for weather sensor

    # while True: 
        
    #     time.sleep(3)
    #     weather_results = readWeatherResults(WEATHER_RESULTS_TXT)
    #     print(weather_results)
    #     if weather_results == 'true':
    #         print('Safe to use')
    #         target_queue = obs_scheduler.getTargetQueue(TARGETS_FILE_PATH)
    #         while target_queue != []:
    #             target = heapq.heappop(target_queue)
    #             # tell mount controller target
    #             with open("pickle/current_target.pickle", "wb") as pickleFile:
    #                 pickle.dump(target, pickleFile)
    #             os.system('python mount/mount_control.py')
    #             # wait for mount to say complete
    #             while True:
    #                 time.sleep(30)
    #                 with open("pickle.current_target.pickle", "rb") as f:
    #                     target = pickle.load(f)
                    
    #                 # TODO: Add safety feature that sends the mount the emergency park command if this loop has ran 10+ min longer than expected observation time (could also send raw serial)

    #                 if target.cmd == 'observation complete':
    #                     break

    #             # get data from camera
    #             # ask storage if full 
    #             #   if full handle or notify somehow
    #             #   else upload or store picture in storage method

    #         # when it is safe to go we need to send 
    #         _writeToFile(WEATHER_RESULTS_TXT, 'exit')
    #         break
    #     else:
    #         print('not safe')

    #         # Things aren't safe so the mount needs to be told to cry
    #         # break

if __name__ == "__main__":
    main()