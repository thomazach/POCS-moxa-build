#!/usr/bin/python3

# TODO: Add color

def main(args):

    PARENT_DIRECTORY = os.path.dirname(__file__).replace('/user_scripts', '')

    if args.force:
        with open(f"{PARENT_DIRECTORY}/pickle/system_info.pickle", "wb") as f:
            systemInfo = {'state': 'off', 'desired_state': 'off'}
            systemInfo = pickle.dump(systemInfo, f)
        time.sleep(0.5)

    with open(f"{PARENT_DIRECTORY}/pickle/system_info.pickle", "rb") as f:
        systemInfo = pickle.load(f)
    
    if systemInfo['state'] == 'off' and systemInfo['desired_state'] == 'off':
        systemInfo['desired_state'] = 'on'

        time.sleep(0.5)
        
        with open(f"{PARENT_DIRECTORY}/pickle/system_info.pickle", "wb") as f:
            pickle.dump(systemInfo, f)
        
        time.sleep(0.5)

        os.system(f'python {PARENT_DIRECTORY}/core/core.py')
    elif systemInfo['state'] == 'on':
        print("System is already running!")
    else:
        print("Contents of system_info.pickle do not match any expected cases. Something has gone wrong, either run first time setup to restore the pickle file or re-install moxa-pocs.")

if __name__ == '__main__':
    import os
    import argparse
    import pickle
    import time

    from schedule import bcolors

    parser = argparse.ArgumentParser(description='''
Put the unit into an automated observation state using the current system settings 
and currently selected schedule file. Changing the settings, editing the schedule
file, or selecting a different scheduling file will not take effect until the
system is taken out of automated obsevation with the 'stop' command.''')
    parser.add_argument('--force', '-f', action='store_true', help='''\
Force the internal system communication to think the unit is in the off state before running start as usual.
This is useful for reseting the system after encountering an error when running the stop or start panoptes-CLI commands.''')
    args = parser.parse_args()
    main(args)
                                     
    

