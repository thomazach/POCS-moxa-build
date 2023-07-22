import os
import sys
import subprocess
import pickle
import multiprocessing
import datetime
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from observational_scheduler.obs_scheduler import target

def requestCameraCommand():
    relative_path = os.path.dirname(os.path.dirname(__file__))
    with open(f"{relative_path}\pickle\current_target.pickle", "rb") as f:
        current_target = pickle.load(f)
    return current_target

def sendTargetObjectCommand(current_target_object, cmd):
    relative_path = os.path.dirname(os.path.dirname(__file__))
    current_target_object.cmd = cmd
    with open(f"{relative_path}\pickle\current_target.pickle", "wb") as f:
        pickle.dump(current_target_object, f)

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
        
        # Clear the camera's RAM to allow for back to back large exposures (tested on 120s)
        cmdClearRAM = f"gphoto2 --port {camera_path} --set-config imageformat=0".split(' ')
        #subprocess.run(cmdClearRAM)
        cmdClearRAM = f"gphoto2 --port {camera_path} --set-config imageformat=9".split(' ')
        #subprocess.run(cmdClearRAM)
        
        cmdArgs = f"gphoto2 --port {camera_path} --set-config iso={iso} --filename {directoryPath}/{observation_dir}/{cam_type}/astro_image_{num_captures}.cr2 --set-config-index shutterpseed=0 --wait-event=1s --set-config-index eosremoterelease=2 --wait-event={exposure_time}s --set-config-index eosremoterelease=4 --wait-event-and-download=2s".split(' ')
        #subprocess.run(cmdArgs)

        # REMOVE IN PRODUCTION, TEST PRINT SINCE ON WINDOWS
        print(cmdArgs)

        num_captures -= 1

def initialize_observation(current_target_object):
    # UNCOMMENT ALL subprocess.run LINES IN PRODUCTION

    format = "%Y-%m-%dT%H:%M:%S"
    timezone = datetime.timezone.utc
    time_and_date = datetime.datetime.now(tz=timezone).strftime(format)

    directoryPath=os.path.dirname(os.path.abspath(__file__)).replace('cameras', 'images')
    cmdMakeObservationDirectory = f"cd {directoryPath}; mkdir {time_and_date}; cd {time_and_date}; mkdir 'Primary_Cam'; mkdir 'Secondary_Cam'".split(' ')
    #subprocess.run(cmdMakeObservationDirectory)

    primary_camera_path, secondary_camera_path = get_camera_paths_dummy() # Replace with get_camera_paths in production
    primary_camera = ('Primary_Cam', primary_camera_path)
    secondary_camera = ('Secondary_Cam', secondary_camera_path)

    cameraSettingsPrimary = [primary_camera[0], primary_camera[1], current_target_object.camera_settings['primary_cam']['num_captures'], current_target_object.camera_settings['primary_cam']['exposure_time'], time_and_date, directoryPath]
    cameraSettingsSecondary = [secondary_camera[0], secondary_camera[1], current_target_object.camera_settings['secondary_cam']['num_captures'], current_target_object.camera_settings['secondary_cam']['exposure_time'], time_and_date, directoryPath]

    if current_target_object.camera_settings['primary_cam']['take_images']:
        primary_cam_process = multiprocessing.Process(target=take_observation, args=([cameraSettingsPrimary]))
        primary_cam_process.start()

    if current_target_object.camera_settings['secondary_cam']['take_images']:
        secondary_cam_process = multiprocessing.Process(target=take_observation, args=([cameraSettingsSecondary]))
        secondary_cam_process.start()
    
    return primary_cam_process, secondary_cam_process

def main():
    current_target = requestCameraCommand()

    if current_target.cmd == 'take images':
<<<<<<< HEAD
            primaryCamProc, secondaryCamProc = initialize_observation(current_target)

            while True:
                # Method to detect if both camera processes or running
                primaryCamProc.join(timeout=0)
                secondaryCamProc.join(timeout=0)
                if not (primaryCamProc.is_alive() or secondaryCamProc.is_alive()):
                    sendTargetObjectCommand(current_target, 'observation complete')
                    break

                current_target = requestCameraCommand()
                match current_target.cmd:
                    case 'emergency park':
                        primaryCamProc.terminate()
                        secondaryCamProc.terminate()
                        break
=======
            initialize_observation(current_target)
            # Need more control over threading, either need a threading control object or use multiprocessing
            # With the current setup, the state/cmd is set to 'observation complete' during the observation. 
            # I can't have one of the camera observation threads running as normal, since I need to check for 
            # emergency exit, and the emergency exit command would be overwritten by observation complete if 
            # I run the secondary cam without threading. Currently its setup to run the second camera without threading,
            # since we don't need to worry about emergency stop cases in intial testing. The same problem also happens
            # when the secondary cameras net observation time is longer than the other
            sendTargetObjectCommand(current_target, 'observation complete')
>>>>>>> 36e1f13 (Added issue comment for camera threading compatibility with target.cmd pickle instance)

if __name__ == '__main__':
    main()
