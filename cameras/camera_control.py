import os
import sys
import subprocess
import pickle
import multiprocessing
import datetime

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

<<<<<<< HEAD
def initialize_observation(current_target_object):
    # UNCOMMENT ALL subprocess.run LINES IN PRODUCTION
=======
<<<<<<< HEAD
def initialize_observation(cam_observation_dict):
=======
def initialize_observation(current_target_object):
    # UNCOMMENT ALL subprocess.run LINES IN PRODUCTION
>>>>>>> f1c2cb2 (Read/write from current_target.pickle and execute observation(print statements for testing))
>>>>>>> 10138a2 (Read/write from current_target.pickle and execute observation(print statements for testing))

    format = "%Y-%m-%dT%H:%M:%S"
    timezone = datetime.timezone.utc
    time_and_date = datetime.datetime.now(tz=timezone).strftime(format)

<<<<<<< HEAD
    directoryPath=os.path.dirname(os.path.abspath(__file__)).replace('cameras', 'images')
    cmdMakeObservationDirectory = f"cd {directoryPath}; mkdir {time_and_date}; cd {time_and_date}; mkdir 'Primary_Cam'; mkdir 'Secondary_Cam'".split(' ')
    #subprocess.run(cmdMakeObservationDirectory)
=======
<<<<<<< HEAD
    #os.sys(f'cd /home/uname/moxa-pocs/images; mkdir {time_and_date}' )
=======
    directoryPath=os.path.dirname(os.path.abspath(__file__)).replace('cameras', 'images')
    cmdMakeObservationDirectory = f"cd {directoryPath}; mkdir {time_and_date}; cd {time_and_date}; mkdir 'Primary_Cam'; mkdir 'Secondary_Cam'".split(' ')
    #subprocess.run(cmdMakeObservationDirectory)
>>>>>>> f1c2cb2 (Read/write from current_target.pickle and execute observation(print statements for testing))
>>>>>>> 10138a2 (Read/write from current_target.pickle and execute observation(print statements for testing))

    primary_camera_path, secondary_camera_path = get_camera_paths_dummy() # Replace with get_camera_paths in production
    primary_camera = ('Primary_Cam', primary_camera_path)
    secondary_camera = ('Secondary_Cam', secondary_camera_path)

<<<<<<< HEAD
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
<<<<<<< HEAD
    if cam_observation_dict['primary_cam']['take_images']:
        threading.Thread(target=take_observation, args=(primary_camera[0], primary_camera[1], cam_observation_dict['primary_cam']['num_captures'], cam_observation_dict['primary_cam']['exposure_time'], time_and_date)).start()

    if cam_observation_dict['secondary_cam']['take_images']:
        take_observation(secondary_camera[0], secondary_camera[1], cam_observation_dict['secondary_cam']['num_captures'], cam_observation_dict['secondary_cam']['exposure_time'], time_and_date)
=======
    cameraSettingsPrimary = [primary_camera[0], primary_camera[1], current_target_object.camera_settings['primary_cam']['num_captures'], current_target_object.camera_settings['primary_cam']['exposure_time'], time_and_date, directoryPath]
    cameraSettingsSecondary = [secondary_camera[0], secondary_camera[1], current_target_object.camera_settings['secondary_cam']['num_captures'], current_target_object.camera_settings['secondary_cam']['exposure_time'], time_and_date, directoryPath]

    if current_target_object.camera_settings['primary_cam']['take_images']:
        threading.Thread(target=take_observation, args=([cameraSettingsPrimary])).start()

    if current_target_object.camera_settings['secondary_cam']['take_images']:
        take_observation(cameraSettingsSecondary)
>>>>>>> f1c2cb2 (Read/write from current_target.pickle and execute observation(print statements for testing))

def main():

    current_target = requestCameraCommand()
    match current_target.cmd:

        case 'take images':
            initialize_observation(current_target)
>>>>>>> 10138a2 (Read/write from current_target.pickle and execute observation(print statements for testing))

if __name__ == '__main__':
    main()