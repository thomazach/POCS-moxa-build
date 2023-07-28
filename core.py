import sys
import os
import threading
import heapq
import time
import random
import pickle
from observational_scheduler import obs_scheduler

WEATHER_RESULTS_TXT = 'weather_results.txt'
TARGETS_FILE_PATH = 'conf_files/test_fields.yaml'
random.seed(time.time_ns)
def writeToFile(PATH, msg):
    file_write = open(PATH, "w")
    file_write.write(msg)
    file_write.close()

def readWeatherResults(PATH):
    weather_results_file_object = open(PATH, 'r')
    weather_results = weather_results_file_object.readline()
    weather_results_file_object.close()
    return weather_results

def checkTargetAvailability(target):
    # Moon avoidance
    return True

def main():
    writeToFile(WEATHER_RESULTS_TXT, 'go')
    writeToFile(WEATHER_RESULTS_TXT, 'true') # Temporarily need to bypass weather module until panoptes team figures out solution for weather sensor
    while True: 
        
        time.sleep(3)
        weather_results = readWeatherResults(WEATHER_RESULTS_TXT)
        print(weather_results)
        if weather_results == 'true':
            print('Safe to use')
            target_queue = obs_scheduler.getTargetQueue(TARGETS_FILE_PATH)
            while target_queue != []:
                target = heapq.heappop(target_queue)
                if not checkTargetAvailability(target.position):
                    continue
                # tell mount controller target
                with open("pickle/current_target.pickle", "wb") as pickleFile:
                    pickle.dump(target, pickleFile)
                os.system('python mount/mount_control.py')
                # wait for mount to say complete
                counter = 0
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
                # remove target from queue


            # when it is safe to go we need to send 
            writeToFile(WEATHER_RESULTS_TXT, 'exit')
            break
        else:
            print('not safe')

            # Things aren't safe so the mount needs to be told to cry
            # break

if __name__ == "__main__":
    main()