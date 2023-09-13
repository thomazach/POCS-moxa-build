#!/usr/bin/python3

def main(args):

    with open(f"{PARENT_DIRECTORY}/pickle/system_info.pickle", "rb") as f:
        systemInfo = pickle.load(f)
    logger.debug("Loaded system_info.pickle")
    
    if systemInfo['state'] == 'on' and systemInfo['desired_state'] == 'on':
        logger.info("Stopping the system.")
        systemInfo['desired_state'] = 'off'

        time.sleep(0.5)
        
        with open(f"{PARENT_DIRECTORY}/pickle/system_info.pickle", "wb") as f:
            pickle.dump(systemInfo, f)
        logger.debug("Wrote desired_state = 'off' to system_info.pickle")
        
        logger.info("Sent shutdown request to the core module.")
        print(bcolors.PURPLE + "Sent shutdown request to the core module." + bcolors.ENDC)

        while True:
            time.sleep(5)
            with open(f"{PARENT_DIRECTORY}/pickle/system_info.pickle", "rb") as f:
                systemInfo = pickle.load(f)

            if systemInfo['state'] == 'off' and systemInfo['desired_state'] == 'off':
                logger.info("System stopped.")
                break
    else:
        print(bcolors.YELLOW + " =WARN= Not in automated observation state." + bcolors.ENDC)

if __name__ == "__main__":
    import os
    import sys
    import argparse
    import pickle
    import time

    from schedule import bcolors

    PARENT_DIRECTORY = os.path.dirname(__file__).replace('/user_scripts', '')
    sys.path.append(PARENT_DIRECTORY)
    from logger.astro_logger import astroLogger

    logger = astroLogger(enable_color=True)

    parser = argparse.ArgumentParser(description='''
Put the unit into an automated observation state using the current system settings 
and currently selected schedule file. Changing the settings, editing the schedule
file, or selecting a different scheduling file will not take effect until the
system is taken out of automated obsevation with the 'stop' command.''')
    args = parser.parse_args()
    main(args)