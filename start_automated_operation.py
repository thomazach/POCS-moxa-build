### File for putting the unit into an automated observation state that is designed to be left unattend for long periods of time

### Import bus structure classes
## Bus functions
def read_safety_sensors(): 
    ### Function that will take in information from environmental data
    ### from temp sensors, AAG cloud watcher, anemometer, or other data
    pass

def is_safe_to_observe():
    ### Process safety sensor data and return a true/false for observation
    pass

def get_target():
    ### from conf_files choose a target and return its name with its RA/DEC coordinates
    pass

def observe_target():
    ### Point the mount at the target RA/DEC points and take images
    pass