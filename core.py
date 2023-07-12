import sys
import threading
import heapq
import time
import random
from observational_scheduler import obs_scheduler

WEATHER_RESULTS_TXT = 'weather_results.txt'
TARGETS_FILE_PATH = 'observational_scheduler/mockData.yaml'
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
    value = random.randint(0, 10)
    return value < 5

def main():
    writeToFile(WEATHER_RESULTS_TXT, 'go')
    while True: 
        
        time.sleep(3)
        weather_results = readWeatherResults(WEATHER_RESULTS_TXT)
        print(weather_results)
        if weather_results == 'true':
            print('Safe to use')
            target_queue = obs_scheduler.getTargetQueue(TARGETS_FILE_PATH)
            while target_queue != []:
                # target = heapq.heappop(target_queue)
                if not checkTargetAvailability(target_queue[0].position):
                    continue
                target = heapq.heappop(target_queue)
                # tell mount controller target
                # wait for mount to say complete
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
