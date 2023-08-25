#!/usr/bin/python3

# TODO: Add color

def main(args):

    PARENT_DIRECTORY = os.path.dirname(__file__).replace('/user_scripts', '')

    with open(f"{PARENT_DIRECTORY}/pickle/system_info.pickle", "rb") as f:
        systemInfo = pickle.load(f)
    
    if systemInfo['state'] == 'off' and systemInfo['desired_state'] == 'off':
        systemInfo['desired_state'] = 'on'

        time.sleep(0.5)
        
        with open(f"{PARENT_DIRECTORY}/pickle/system_info.pickle", "wb") as f:
            pickle.dump(systemInfo, f)
        
        time.sleep(0.5)

        os.system(f'python {PARENT_DIRECTORY}/core/core.py')
    

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
    args = parser.parse_args()
    main(args)
                                     
    

