#!/usr/bin/python3
from schedule import bcolors

def main(args):

    settingsFile = os.path.realpath(__file__).replace('user_scripts/settings.py', '/conf_files/settings.yaml')

    with open(settingsFile, "r") as f:
        settings = yaml.safe_load(f)

    if args.latitude:
        settings["LATITUDE"] = args.latitude[0]
    
    if args.longitude:
        settings["LONGITUDE"] = args.longitude[0]

    if args.elevation:
        settings["ELEVATION"] = args.elevation[0]

    if args.set_logging_level:
        settings["DEBUG_MESSAGE_LEVEL"] = args.set_logging_level[0]

    if args.show:
        print("---------------   Current system settings   ---------------")
        for key in settings.keys():
            print(f"{key} : {bcolors.OKBLUE}{settings[key]}{bcolors.ENDC}")
        print(bcolors.YELLOW + "Changes will not apply during automated operation" + bcolors.ENDC)

    with open(settingsFile, "w") as f:
        yaml.dump(settings, f)

if __name__ == "__main__":
    import argparse
    import os
    import yaml

    parser = argparse.ArgumentParser(description='Edit system settings.', formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--latitude', '-lat', action='store', nargs=1, type=float,
                        help='''\
    Set the latitude of the telescope with a decimal degree. Will not update if in automated observation state. 
    Example: 
                        >> settings --latitude 44.56725
    ''')
    parser.add_argument('--longitude', '-long', action='store', nargs=1,
                        help='''\
    Set the longitude of the telescope with a decimal degree. Will not update if in automated observation state. 
    Example: 
                        >> settings --longitude -123.28925
    ''')
    parser.add_argument('--elevation', '--height', action='store', nargs=1,
                        help='''\
    Set the elevation above sea level of the telescope in meters. Will not update if in automated observation state. 
    Example: 
                        >> settings --elevation 72
    ''')
    parser.add_argument('-set_log', '--set_logging_level', action='store', nargs=1, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help='''\
    Set the logging level of the system. Inputs: "DEBUG", "INFO", "WARNING", "ERROR", or "CRITICAL"
    Example:
                        >> settings --set_log INFO
    ''')
    parser.add_argument('--show', '-ls', action='store_true',
                        help='''List the current settings.''')

    args = parser.parse_args()
    main(args)


    
