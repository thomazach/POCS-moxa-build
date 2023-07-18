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
    out = out.stdout.decode('utf-8')
    out = out.translate({ord(c): None for c in string.whitespace})
    out = out.split("CanonEOS100D", -1)

    primary_camera_path = out[1]
    secondary_camera_path = out[2]

    return primary_camera_path, secondary_camera_path

def take_observation(cam_type, camera_path, num_captures, exposure_time, observation_dir, iso=1):
    if num_captures <= 0:
        raise Exception("Bad observation data: num_captures must be positive")

    while True:
        if num_captures == 0:
            break

        # UNCOMMENT IN PRODUCTION
        #os.sys(f"gphoto2 --port {camera_path} --set-config iso={iso} --filename /home/uname/moxa-pocs/images/{observation_dir}/{cam_type}/astro_image_{num_captures}.cr2 --set-config-index shutterpseed=0 --wait-event=1s --set-config-index eosremoterelease=2 --wait-event={exposure_time}s --set-config-index eosremoterelease=4 --wait-event-and-download=2s")
        
        time.sleep(exposure_time) # May or may not be necessary, don't have tesing setup yet

        # TEST PRINT SINCE ON WINDOWS
        print(f"gphoto2 --port {camera_path} --set-config iso={iso} --filename /home/uname/moxa-pocs/images/{observation_dir}/{cam_type}/astro_image_{num_captures}.cr2 --set-config-index shutterpseed=0 --wait-event=1s --set-config-index eosremoterelease=2 --wait-event={exposure_time}s --set-config-index eosremoterelease=4 --wait-event-and-download=2s")

        # UNCOMMENT IN PRODUCTION
        # Clear the camera's RAM in a hacky way to allow for back to back large exposures (tested on 120s)
        #os.sys(f"gphoto2 --port {camera_path} --set-config imageformat=0")
        #os.sys(f"gphoto2 --port {camera_path} --set-config imageformat=9")
        num_captures -= 1

def initialize_observation(cam_observation_dict):

    format = "%Y-%m-%dT%H:%M:%S"
    timezone = datetime.timezone.utc
    time_and_date = datetime.datetime.now(tz=timezone).strftime(format)

    #os.sys(f'cd /home/uname/moxa-pocs/images; mkdir {time_and_date}' )

    primary_camera_path, secondary_camera_path = get_camera_paths_dummy() # Replace with get_camera_paths in production
    primary_camera = ('Primary_Cam', primary_camera_path)
    secondary_camera = ('Secondary_Cam', secondary_camera_path)

    if cam_observation_dict['primary_cam']['take_images']:
        threading.Thread(target=take_observation, args=(primary_camera[0], primary_camera[1], cam_observation_dict['primary_cam']['num_captures'], cam_observation_dict['primary_cam']['exposure_time'], time_and_date)).start()

    if cam_observation_dict['secondary_cam']['take_images']:
        take_observation(secondary_camera[0], secondary_camera[1], cam_observation_dict['secondary_cam']['num_captures'], cam_observation_dict['secondary_cam']['exposure_time'], time_and_date)

config = give_dummy_command_data()

initialize_observation(config)
