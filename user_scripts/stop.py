#!/usr/bin/python3

def main(args):

    PARENT_DIRECTORY = os.path.dirname(__file__).replace('/user_scripts', '')

    with open(f"{PARENT_DIRECTORY}/pickle/system_info.pickle", "rb") as f:
        systemInfo = pickle.load(f)
    
    if systemInfo['state'] == 'on' and systemInfo['desired_state'] == 'on':
        systemInfo['desired_state'] = 'off'

        time.sleep(0.5)
        
        with open(f"{PARENT_DIRECTORY}/pickle/system_info.pickle", "wb") as f:
            pickle.dump(systemInfo, f)
        
        # TODO: Add logging
        print(bcolors.PURPLE + "Sent shutdown request to the core module." + bcolors.ENDC)

        while True:
            time.sleep(5)
            with open(f"{PARENT_DIRECTORY}/pickle/system_info.pickle", "rb") as f:
                systemInfo = pickle.load(f)

            if systemInfo['state'] == 'off' and systemInfo['desired_state'] == 'off':
                break
    else:
        print(bcolors.YELLOW + " =WARN= Not in automated observation state." + bcolors.ENDC)

if __name__ == "__main__":
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