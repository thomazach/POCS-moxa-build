import sys
import threading
import heapq
import time
from observational_scheduler import obs_scheduler

WEATHER_RESULTS_TXT = 'weather_results.txt'
TARGETS_FILE_PATH = 'observational_scheduler/mockData.yaml'

def writeToFile(PATH, msg):
    fileWrite = open(PATH, "w")
    fileWrite.write(msg)
    fileWrite.close()

def main():
    # this is main

    # how to get targets out of the obs scheduler queue
    # test = obs_scheduler.getTargetQueue(TARGETS_FILE_PATH)
    # while test != []:
    #     print(heapq.heappop(test))

    while True: 
        weather_results_file_object = open(WEATHER_RESULTS_TXT, 'r')

        weather_results_file_object.write('go') # tell weather do the thing
        time.sleep(1)
        weather_results = weather_results_file_object.readline()
        if weather_results == 'true\n':
            print('Safe to use')

            # when it is safe to go we need to send 
            break
        else:
            print('not safe')

            # Things aren't safe so the mount needs to be told to cry
            break



if __name__ == "__main__":
    main()
