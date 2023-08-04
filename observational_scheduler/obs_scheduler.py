import os
import heapq
import yaml
from yaml.loader import SafeLoader

DATA_FILE_DEFAULT_PATH = os.path.dirname(__file__).replace('observational_scheduler', 'conf_files/observations.yaml')#'conf_files/test_fields.yaml')

class target:

    def __init__(self, name, position, camera_settings, priority = 0, observation_notes = None, command = 'slew to target')->None:
        self.name = name
        self.observation_notes = observation_notes
        self.position = position
        self.camera_settings = camera_settings
        self.cmd = command

        # we store priorities as negative numbers because heapq is a min heap
        self.priority = 0 - priority
    
    def __lt__(self, other):
        return self.priority < other.priority
    
    def __le__(self, other):
        return self.priority <= other.priority
    
    def __eq__(self, other):
        if self.name == other.name and self.priority == other.priority and self.position == other.position:
            return True
        return False
    
    def __gt__(self, other):
        return self.priority > other.priority
    
    def __ge__(self, other):
        return self.priority >= other.priority
    
    def __str__(self):
        return f'---\npriority={0 - self.priority}\nname={self.name}\nposition={self.position}\ncamera_settings={self.camera_settings}\nobservation_notes={self.observation_notes}\n---'
    
def createObservationList(observationDict, PATH = DATA_FILE_DEFAULT_PATH):
    with open(PATH, 'w') as file:
        observation = yaml.dump(observationDict, file)

def getTargetQueue(PATH = DATA_FILE_DEFAULT_PATH):
    pQueue = []
    heapq.heapify(pQueue)
    dataDict = 0
    with open(PATH) as file:
        dataDict = yaml.load(file, Loader=SafeLoader)
    for key, entry in dataDict.items():
        name = key
        obsNote = entry['note']
        prio = entry['priority']
        position = {'ra': entry['ra'], 'dec' :entry['dec']}
        cameraSettings = {'primary_cam' : entry['primary_cam'], 'secondary_cam' : entry['secondary_cam']}
        command = entry['cmd']

        heapq.heappush(pQueue, target(name, position, cameraSettings, priority=prio, observation_notes=obsNote, command=command))
    return pQueue

def getTargetList(PATH = DATA_FILE_DEFAULT_PATH):
    result = []
    with open(PATH) as file:
        dataDict = yaml.load(file, Loader=SafeLoader)
    for key, entry in dataDict.items():
        name = key
        obsNote = entry['note']
        prio = entry['priority']
        position = {'ra': entry['ra'], 'dec' :entry['dec']}
        cameraSettings = {'primary_cam' : entry['primary_cam'], 'secondary_cam' : entry['secondary_cam']}
        command = entry['cmd']

        result.append(target(name, position, cameraSettings, priority=prio, observation_notes=obsNote, command=command))

    return result

