#!/usr/bin/python3
# TODO: Implement testing mode in the mount module that stops it from calling 
# the camera module. Update documentation for the mount module as well.
def main(args):

    if args.weather:
        print(bcolors.FAIL + "Weather module is still a work in progress." + bcolors.ENDC)
        return
    
    ### Testing any hardware module will require that we check that the system isn't 
    ### already running, load the schedule file specified in settings.yaml, and create a target
    ### queue
    with open(f"{PARENT_DIRECTORY}/pickle/system_info.pickle", "rb") as f:
        systemInfo = pickle.load(f)
    
    if systemInfo['state'] == 'on':
        print(bcolors.FAIL + "The system is running in its automatic state! Stop if with '>>stop' before testing modules!" + bcolors.ENDC)
        logger.warning("Can not perform hardware test, system is running.")
        return
    
    with open(f"{PARENT_DIRECTORY}/conf_files/settings.yaml", 'r') as f:
        settings = yaml.safe_load(f)

    print(bcolors.OKCYAN + "Creating target list from the schedule file: " + settings['TARGET_FILE'] + bcolors.ENDC)
    targetQueue = obs_scheduler.getTargetQueue(f"{PARENT_DIRECTORY}/conf_files/targets/{settings['TARGET_FILE']}")
    print(bcolors.OKGREEN + "Done." + bcolors.ENDC)
    logger.info(f"Succesfully created target queue using the schedule file: {settings['TARGET_FILE']}") 

    # Iterate through the targets and call the requested module for each target
    while targetQueue != []:
        target = heapq.heappop(targetQueue)
        logger.debug(f"Target instance: {target}")

        print(bcolors.OKCAYN + "Giving system the next target." + bcolors.ENDC)
        with open(f"{PARENT_DIRECTORY}/pickle/current_target.pickle", "rb") as f:
            pickle.dump(target, f)
        print(bcolors.OKGREEN + "Done." + bcolors.ENDC)
        logger.info("Updated current_target.pickle with target information.")

        # Perform tests based on which module was requested
        on = True  # while loop variable
        if args.camera:
            # Call camera_control.py
            print(bcolors.OKCYAN + "Calling camera module to take pictures with the current target's settings." + bcolors.ENDC)
            Popen(['python3', f"{PARENT_DIRECTORY}/cameras/camera_control.py"])
            print(bcolors.OKGREEN + "Done." + bcolors.ENDC)
            logger.debug("Called camera_control.py")

            # Wait for all images to be taken
            print(bcolors.OKCYAN + "Waiting for the camera to take images of the current target." + bcolors.ENDC)
            while on:
                with open(f"{PARENT_DIRECTORY}/pickle/current_target.pickle", "rb") as f:
                    target = pickle.load(f)
                
                if target.cmd == 'observation complete':
                    print(bcolors.OKGREEN + "Done." + bcolors.ENDC)
                    break
                time.sleep(10)

        if args.mount:
            # Throw error message if corrective tracking/plate solving is enabled, since this feature
            # inherently requires communication between the mount and cameras.
            if settings['PLATE_SOLVE'] in (None, "None", 0, False):
                print(bcolors.FAIL + "Can't test mount module independently from system because plate solving is enabled. Temporarily disable plate solving in your settings to continue." + bcolors.ENDC)
                logger.warning("Failed to test mount module because plate solving was enabled.")
                return

            # Turn on testing mode, which is really just a bool that stops the mount module from calling the camera module
            with open(f"{PARENT_DIRECTORY}/pickle/system_info.pickle", "rb") as f:
                systemInfo = pickle.load(f)

            systemInfo['testing_mode'] = True

            with open(f"{PARENT_DIRECTORY}/pickle/system_info.pickle", "wb") as f:
                pickle.dump(systemInfo, f)

            # Call mount module and wait for slewing to complete (aka ready to 'take images')
            print(bcolors.OKCYAN + "Calling mount module with the current target's settings." + bcolors.ENDC)
            Popen('python3' f"{PARENT_DIRECTORY}/mount/mount_control.py")
            print(bcolors.OKGREEN + "Done." + bcolors.ENDC)
            logger.debug("Called the mount module.")
            
            print(bcolors.OKCYAN + "Waiting for the mount to finish slewing to the current target.")
            time.sleep(5)
            while on:
                with open(f"{PARENT_DIRECTORY}/pickle/current_target.pickle", "rb") as f:
                    target = pickle.load(f)
                
                if target.cmd == 'take images':
                    print(bcolors.OKGREEN + "Done." + bcolors.ENDC)

                    print(bcolors.OKCYAN + "Simulating the end of camera observation by sending the 'observation complete' command to the mount module.")
                    with open(f"{PARENT_DIRECTORY}/pickle/current_target.pickle", "wb") as f:
                        target.cmd = 'observation complete'
                        pickle.dump(target, f)
                    print(bcolors.OKGREEN + "Done." + bcolors.ENDC)

                    print(bcolors.OKCYAN + "Waiting for the mount to park." + bcolors.ENDC)
                    while on:
                        with open(f"{PARENT_DIRECTORY}/pickle/current_target.pickle", "rb") as f:
                            target = pickle.load(f)
                        
                        if target.cmd == 'parked':
                            print(bcolors.OKGREEN + "Done." + bcolors.ENDC)
                            on = False

                            # Turn off testing mode
                            systemInfo['testing_mode'] = True
                            with open(f"{PARENT_DIRECTORY}/pickle/system_info.pickle", "wb") as f:
                                pickle.dump(systemInfo, f)
                    
                        time.sleep(10)
                time.sleep(10)

    # After test success messages/further instructions
    if args.camera:
        print(bcolors.OKGREEN + f"Finished testing the camera module. Look in {PARENT_DIRECTORY}/images to see the raw images." + bcolors.ENDC)
    
    if args.mount:
        print(bcolors.OKGREEN + "Finished testing the mount module." + bcolors.ENDC)

if __name__ == "__main__":
    import os
    import sys
    import time
    import argparse
    import yaml
    import pickle
    import heapq

    from schedule import bcolors
    from subprocess import Popen

    PARENT_DIRECTORY = os.path.dirname(__file__).replace('/user_scripts', '')
    sys.path.append(PARENT_DIRECTORY)

    from logger.astro_logger import astroLogger
    from observational_scheduler import obs_scheduler

    logger = astroLogger(enable_color=True)

    parser = argparse.ArgumentParser(description="Test system hardwardware modules individually. Only one module can be tested at a time.")
    modules = parser.add_mutually_exclusive_group

    modules.add_argument('--camera, -cam', action='store_true', help='''\
Test the cameras by having them take images independently of the rest of the system. Cameras will take images as 
instructed by the currently selected schedule file. (Images will be taken for all targets, and all
camera settings will match those specified by the schedule file.)''')
    
    modules.add_argument('--mount', action='store_true', help='''\
Test the mount by having it slew to targets independently without relying on other modules. The mount will slew to targets
as instructed by the currently selected schedule file. For each target, the mount will go to the home position, slew to the
target coordinates, start tracking, slew to the home position, and then move to the park position with it's cameras facing 
the ground.''')
    
    modules.add_argument('--weather', action='store_true', help='Placeholder. Is not weather is not implemented command has no effect.')
    
    args = parser.parse_args()
    main(args)