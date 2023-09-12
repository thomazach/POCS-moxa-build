import os
import sys
import subprocess
import pickle
import multiprocessing
import datetime
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from observational_scheduler.obs_scheduler import target
from logger.astro_logger import astroLogger

def requestCameraCommand():
    relative_path = os.path.dirname(os.path.dirname(__file__))
    with open(f"{relative_path}/pickle/current_target.pickle", "rb") as f:
        current_target = pickle.load(f)

    logger.debug(f"Read current_target.pickle data: {current_target}")
    return current_target

def sendTargetObjectCommand(current_target_object, cmd):
    relative_path = os.path.dirname(os.path.dirname(__file__))
    current_target_object.cmd = cmd
    with open(f"{relative_path}/pickle/current_target.pickle", "wb") as f:
        pickle.dump(current_target_object, f)
    logger.debug(f"Updated status of current_target.pickle to:\n {current_target_object}")

def get_camera_paths():
    logger.info("Finding cameras using gphoto2...")
    out = subprocess.run(["gphoto2", "--auto-detect"], stdout=subprocess.PIPE)
    gphotoString = out.stdout.decode('utf-8')

    for char in [' ', '-', 'Model', 'Port', '\n']:
        gphotoString = gphotoString.replace(char, '')

    usbIndex = None
    cameraPaths = []
    while not usbIndex == -1:
        usbIndex = gphotoString.find("usb")
        cameraPaths.append(gphotoString[usbIndex:usbIndex+11])
        gphotoString = gphotoString[usbIndex+11:]
    cameraPaths = list(filter(None, cameraPaths))

    logger.info(f"Found cameras with paths: {cameraPaths}")

    try:
        primary_camera_path, secondary_camera_path = cameraPaths
        return primary_camera_path, secondary_camera_path
    except ValueError:
        print("Issue detecting cameras. Check power, camera settings, and the output of 'gphoto2 --auto-detect'")
        logger.error("Could not detect the cameras.")
    except Exception as e:
        print("=ERROR=", e)
        logger.critical(e)

def take_observation(cameraSettings, iso=1):
    cam_type, camera_path, num_captures, exposure_time, observation_dir, directoryPath = cameraSettings

    if num_captures <= 0:
        raise Exception("Bad observation data: num_captures must be a positive non-zero integer")
    i = num_captures
    while True:
        if i == 0:
            break

        cmdArgs = f"gphoto2 --port {camera_path} --set-config iso={iso} --filename {directoryPath}/{observation_dir}/{cam_type}/astro_image_{num_captures - i}.cr2 --set-config-index shutterspeed=0 --wait-event=1s --set-config-index eosremoterelease=2 --wait-event={exposure_time}s --set-config-index eosremoterelease=4 --wait-event-and-download=2s".split(' ')
        subprocess.run(cmdArgs)
        logger.info(f"Taking picture with an exposure time of {exposure_time} with an ISO setting index of {iso}.")

        i -= 1

def blank_process():
    pass

def initialize_observation(current_target_object):

    logger.info("Initializing camera processes for the observation.")

    format = "%Y-%m-%dT%H:%M:%S"
    timezone = datetime.timezone.utc
    time_and_date = datetime.datetime.now(tz=timezone).strftime(format)

    directoryPath=os.path.dirname(os.path.abspath(__file__)).replace('cameras', 'images')
    cmdMakeObservationDirectory = f"mkdir {time_and_date}; mkdir {time_and_date}/Primary_Cam; mkdir {time_and_date}/Secondary_Cam"
    subprocess.Popen(cmdMakeObservationDirectory, shell=True, cwd=directoryPath)

    logger.debug("Created time-stamped directories for images.")

    primary_camera_path, secondary_camera_path = get_camera_paths()
    primary_camera = ('Primary_Cam', primary_camera_path)
    secondary_camera = ('Secondary_Cam', secondary_camera_path)

    cameraSettingsPrimary = [primary_camera[0], primary_camera[1], current_target_object.camera_settings['primary_cam']['num_captures'], current_target_object.camera_settings['primary_cam']['exposure_time'], time_and_date, directoryPath]
    cameraSettingsSecondary = [secondary_camera[0], secondary_camera[1], current_target_object.camera_settings['secondary_cam']['num_captures'], current_target_object.camera_settings['secondary_cam']['exposure_time'], time_and_date, directoryPath]

    logger.info("Created cameras settings for this target.")

    primary_cam_process = None
    secondary_cam_process = None
    if current_target_object.camera_settings['primary_cam']['take_images']:
        primary_cam_process = multiprocessing.Process(target=take_observation, args=([cameraSettingsPrimary]))
        primary_cam_process.start()
    else:
        primary_cam_process = multiprocessing.Process(target=blank_process)
        primary_cam_process.start()

    if current_target_object.camera_settings['secondary_cam']['take_images']:
        secondary_cam_process = multiprocessing.Process(target=take_observation, args=([cameraSettingsSecondary]))
        secondary_cam_process.start()
    else:
        secondary_cam_process = multiprocessing.Process(target=blank_process)
        secondary_cam_process.start()

    logger.info("Started camera processes.")
    return primary_cam_process, secondary_cam_process

def main():
    logger.info("Camera module has been activated.")
    current_target = requestCameraCommand()

    if current_target.cmd == 'take images':
            logger.info("Recieved command from core to take images.")
            primaryCamProc, secondaryCamProc = initialize_observation(current_target)

            while True:
                # Method to detect if both camera processes are running
                primaryCamProc.join(timeout=0)
                secondaryCamProc.join(timeout=0)
                if not (primaryCamProc.is_alive() or secondaryCamProc.is_alive()):
                    logger.info("Cameras have finished taking pictures")
                    sendTargetObjectCommand(current_target, 'observation complete')
                    break

                current_target = requestCameraCommand()
                match current_target.cmd:
                    case 'emergency park':
                        logger.info("Emergency park command recieved. Stopping the camera processes.")
                        primaryCamProc.terminate()
                        secondaryCamProc.terminate()
                        break
                    case 'parked':
                        logger.info("Mount is parked. Exiting.")
                        break

if __name__ == '__main__':
    logger = astroLogger(enable_color=True)
    main()
