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

def readWeatherResults(PATH):
    weather_results_file_object = open(PATH, 'r')
    weather_results = weather_results_file_object.readline()
    weather_results_file_object.close()
    return weather_results

def main():

    # how to get targets out of the obs scheduler queue
    # test = obs_scheduler.getTargetQueue(TARGETS_FILE_PATH)
    # while test != []:
    #     print(heapq.heappop(test))
    writeToFile(WEATHER_RESULTS_TXT, 'go')
    while True: 
        
        time.sleep(3)
        weatherResults = readWeatherResults(WEATHER_RESULTS_TXT)
        print(weatherResults)
        if weatherResults == 'true':
            print('Safe to use')

            # when it is safe to go we need to send 
            writeToFile(WEATHER_RESULTS_TXT, 'exit')
            break
        else:
            print('not safe')

            # Things aren't safe so the mount needs to be told to cry
            # break



if __name__ == "__main__":
    main()
