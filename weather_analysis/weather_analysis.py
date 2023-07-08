#THIS IS CURRENTLY A MOCK NOT FUNCTIONAL
import time
import heapq
import yaml
from yaml.loader import SafeLoader

WEATHER_MOCK_DATA = 'weatherMock.yaml'
WEATHER_RESULTS_TXT = '../weather_results.txt'

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
        return '|'+str(0 - self.priority)+'|    temperature='+self.temperature+', moisture='+self.moisture+', windSpeed='+self.windSpeed
    
def writeToFile(PATH, msg):
    fileWrite = open(PATH, "w")
    fileWrite.write(msg)
    fileWrite.close()

def readFromFile(PATH):
    file_object = open(PATH, 'r')
    results = file_object.readline()
    file_object.close()
    return results



def main():

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

    while True: 
        weather_results = readFromFile(WEATHER_RESULTS_TXT)
        match weather_results:
            case 'go':
                writeToFile(WEATHER_RESULTS_TXT, 'true')
                time.sleep(2)
            case 'exit':
                writeToFile(WEATHER_RESULTS_TXT, '')
                break
            case _:
                time.sleep(3)
        

           
if __name__ == "__main__":
    main()
