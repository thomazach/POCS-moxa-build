import os
import heapq
import yaml
from yaml.loader import SafeLoader

DATA_FILE_DEFAULT_PATH = os.path.dirname(__file__).replace('observational_scheduler', 'conf_files/test_fields.yaml')

class target:

    def __init__(self, name, position, priority = 0)->None:
        self.name = name
        self.position = position

        # we store priorities as negative numbers because heapq is a min heap
        self.priority = 0 - priority


    def __lt__(self, other):
        return self.priority < other.priority
    
    def __eq__(self, other):
        if self.name == other.name and self.priority == other.priority and self.position == other.position:
            return True
        return False
    
    def __str__(self):
        return f'priority={0 - self.priority} name={self.name}, position={self.position}'

def getTargetQueue(PATH):
    pQueue = []
    heapq.heapify(pQueue)
    dataDict = 0
    with open(DATA_FILE_DEFAULT_PATH) as file:
        dataDict = yaml.load(file, Loader=SafeLoader)
    for key, entry in dataDict.items():
        name = key
        prio = entry['priority']
        position = (entry['ra'], entry['dec'])

        heapq.heappush(pQueue, target(name, position, prio))
    return pQueue