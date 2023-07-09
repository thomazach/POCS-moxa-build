#THIS IS CURRENTLY A MOCK NOT FUNCTIONAL
import threading
import  queue
import time
import heapq
import yaml
from yaml.loader import SafeLoader

WEATHER_MOCK_DATA = 'weatherMock.yaml'
WEATHER_RESULTS_TXT = '../weather_results.txt'

exit_flag = 0
queue_lock = threading.Lock()
work_queue = queue.Queue(10)
threads = []

# This class is here only for the mocks since I don't know what 
# the api/equipment will output or how
class weatherEvent:
    def __init__(self, temperature, moisture, windSpeed, priority = 0)->None:
        self.temperature = temperature
        self.moisture = moisture
        self.windSpeed = windSpeed
        # we store priorities as negative numbers because heapq is a min heap
        self.priority = 0 - priority
    def __lt__(self, other):
        return self.priority < other.priority
    def __eq__(self, other):
        if self.temperature == other.temperature and self.moisture == other.moisture and self.windSpeed == other.windSpeed and self.priority == other.priority:
            return True
        return False
    def __str__(self):
        return '|'+str(0 - self.priority)+'|    temperature='+str(self.temperature)+', moisture='+str(self.moisture)+', windSpeed='+str(self.windSpeed)
    
def writeToFile(PATH, msg):
    fileWrite = open(PATH, "w")
    fileWrite.write(msg)
    fileWrite.close()

def readFromFile(PATH):
    file_object = open(PATH, 'r')
    results = file_object.readline()
    file_object.close()
    return results

def getEventsQueue():
    # Create this priority queue that will act as our mock api calls
    # Will analyze data from a file containing mock weather events
    # these will then be fed on a timer into the program
    pQueue = []
    data = 0
    with open(WEATHER_MOCK_DATA) as file:
        data = yaml.load(file, Loader=SafeLoader)
    for entry in data:
        temperatrue = entry['temperature']
        moisture = entry['moisture']
        windSpeed = entry['windSpeed']
        priority = entry['priority']
        heapq.heappush(pQueue, weatherEvent(temperatrue, moisture, windSpeed, priority))
    return pQueue

class myThread(threading.Thread):
    def __init__(self, threadID, name, queue):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.queue = queue
    def run(self):
        print("Starting " + self.name)
        process_data(self.name, self.queue, getEventsQueue())
        print("Exiting " + self.name)
        
def process_data(threadName, queue, eventsQueue):
    while not exit_flag and eventsQueue != []:
        item = heapq.heappop(eventsQueue)
        time.sleep(5)
        queue.put(item)
        print('put item: ', item)
        time.sleep(1)

def main():
    threadCount = 1
    thread = myThread(threadCount, 'Mocks', work_queue)
    thread.start()
    threads.append(thread)
    threadCount += 1

    while True: 
        weather_results = readFromFile(WEATHER_RESULTS_TXT)
        match weather_results:
            case 'go':
                condition = work_queue.get()
                print(condition)
                if condition.temperature >= 100 or condition.moisture < 10 or condition.windSpeed >= 120:
                    writeToFile(WEATHER_RESULTS_TXT, 'false')
                else:
                    writeToFile(WEATHER_RESULTS_TXT, 'true')
            case 'exit':
                exit_flag = 1
                writeToFile(WEATHER_RESULTS_TXT, '')
                break
            case _:
                try:
                    condition = work_queue.get(True, 10)
                except:
                    exit_flag = 1
                    writeToFile(WEATHER_RESULTS_TXT, '')
                    break
                print(condition)
                if condition.temperature >= 100 or condition.moisture < 10 or condition.windSpeed >= 120:
                    print('false')
                    writeToFile(WEATHER_RESULTS_TXT, 'false')
                else:
                    print('true')
                    writeToFile(WEATHER_RESULTS_TXT, 'true')
        

           
if __name__ == "__main__":
    main()
