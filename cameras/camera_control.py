import threading
import time
import string
import subprocess
import os
import datetime


def give_dummy_command_data():
    '''
    Recieves the following from pocs.observational_scheduler:
    -number of images to take in this observation
    -exposure time of each image
    -what combination of cameras to take images with

    Example .yaml:

    observation:
        priority: 100
        primary_cam: 
            take_images: True
            num_captures: 10
            exposure_time: 120

        secondary_cam:
            take_images: True
            num_captures: 40
            exposure_time: 30
    '''
    return dict({'primary_cam': {'take_images': True, 'num_captures': 10, 'exposure_time': 12}, 'secondary_cam': {'take_images': True, 'num_captures': 40, 'exposure_time': 3}})

def get_camera_paths_dummy():
    return "usb:001,007", "usb:001,008"

def get_camera_paths():
    print("Finding cameras using gphoto2...")
    out = subprocess.run(["gphoto2", "--auto-detect"], stdout=subprocess.PIPE)
    cameraPaths = out.stdout.decode('utf-8')

    for charsToRemove in ['Model', 'Port', 'n', '\n', ' ']:
        cameraPaths = cameraPaths.replace(charsToRemove, '')

    cameraPaths = cameraPaths.split("CanonEOS100D")

    primary_camera_path, secondary_camera_path = cameraPaths

    return primary_camera_path, secondary_camera_path

def take_observation(cameraSettings, iso=1):
    cam_type, camera_path, num_captures, exposure_time, observation_dir, directoryPath = cameraSettings
    
    if num_captures <= 0:
        raise Exception("Bad observation data: num_captures must be a positive non-zero integer")

    while True:
        # UNCOMMENT ALL subprocess.run LINES IN PRODUCTION
        if num_captures == 0:
            break
        
        # Clear the camera's RAM in a hacky way to allow for back to back large exposures (tested on 120s)
        cmdClearRAM = f"gphoto2 --port {camera_path} --set-config imageformat=0".split(' ')
        #subprocess.run(cmdClearRAM)
        cmdClearRAM = f"gphoto2 --port {camera_path} --set-config imageformat=9".split(' ')
        #subprocess.run(cmdClearRAM)
        
        cmdArgs = f"gphoto2 --port {camera_path} --set-config iso={iso} --filename {directoryPath}/{observation_dir}/{cam_type}/astro_image_{num_captures}.cr2 --set-config-index shutterpseed=0 --wait-event=1s --set-config-index eosremoterelease=2 --wait-event={exposure_time}s --set-config-index eosremoterelease=4 --wait-event-and-download=2s".split(' ')
        #subprocess.run(cmdArgs)

        # REMOVE IN PRODUCTION, TEST PRINT SINCE ON WINDOWS
        print(cmdArgs)

        num_captures -= 1

def initialize_observation(cam_observation_dict):
    # UNCOMMENT ALL subprocess.run LINES IN PRODUCTION

    format = "%Y-%m-%dT%H:%M:%S"
    timezone = datetime.timezone.utc
    time_and_date = datetime.datetime.now(tz=timezone).strftime(format)

    directoryPath=os.path.dirname(os.path.abspath(__file__)).replace('cameras', 'images')
    cmdMakeObservationDirectory = f"cd /home/uname/moxa-pocs/images; mkdir {time_and_date}".split(' ')
    #subprocess.run(cmdMakeObservationDirectory)

    primary_camera_path, secondary_camera_path = get_camera_paths_dummy() # Replace with get_camera_paths in production
    primary_camera = ('Primary_Cam', primary_camera_path)
    secondary_camera = ('Secondary_Cam', secondary_camera_path)

    cameraSettings = [primary_camera[0], primary_camera[1], cam_observation_dict['primary_cam']['num_captures'], cam_observation_dict['primary_cam']['exposure_time'], time_and_date, directoryPath]

    if cam_observation_dict['primary_cam']['take_images']:
        threading.Thread(target=take_observation, args=([cameraSettings])).start()

    if cam_observation_dict['secondary_cam']['take_images']:
        take_observation(cameraSettings)

config = give_dummy_command_data()

initialize_observation(config)
