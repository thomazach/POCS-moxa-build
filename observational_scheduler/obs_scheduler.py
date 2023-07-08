import heapq
import yaml
from yaml.loader import SafeLoader

DATA_FILE_DEFAULT_PATH = 'observational_scheduler/mockData.yaml'

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
        return 'priority='+str(0 - self.priority)+', name='+self.name+', position='+self.position

def getTargetQueue(PATH):
    pQueue = []
    heapq.heapify(pQueue)
    data = 0
    with open(DATA_FILE_DEFAULT_PATH) as file:
        data = yaml.load(file, Loader=SafeLoader)
    for entry in data:
        prio = entry['observation']['priority']
        name = entry['field']['name']
        position = entry['field']['position']

        heapq.heappush(pQueue, target(name, position, prio))
    return pQueue