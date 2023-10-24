#!/usr/bin/python3

def main(args):

    settingsFile = os.path.realpath(__file__).replace('user_scripts/settings.py', '/conf_files/settings.yaml')

    with open(settingsFile, "r") as f:
        settings = yaml.safe_load(f)

    if args.latitude:
        settings["LATITUDE"] = str(args.latitude[0])
    
    if args.longitude:
        settings["LONGITUDE"] = str(args.longitude[0])

    if args.elevation:
        settings["ELEVATION"] = float(args.elevation[0])

    if args.set_logging_level:
        settings["DEBUG_MESSAGE_LEVEL"] = args.set_logging_level[0]

    if args.plate_solve:
        settings['PLATE_SOLVE'] = args.plate_solve[0]

    if args.abort_after_failure_to_plate_solve:
        settings['ABORT_AFTER_FAILED_SOLVE'] = args.abort_after_failure_to_plate_solve[0]

    if args.simulators:
        settings['SIMULATORS'] = args.simulators[0]

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

    from schedule import bcolors

    parser = argparse.ArgumentParser(description='Edit system settings.', formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--latitude', '-lat', action='store', nargs=1, type=float, metavar='<latitude>',
                        help='''\
    Set the latitude of the telescope with a decimal degree. Will not update if in automated observation state. 
    Example: 
                        >> settings --latitude 44.56725
    ''')
    parser.add_argument('--longitude', '-long', action='store', nargs=1, metavar='<longitude>',
                        help='''\
    Set the longitude of the telescope with a decimal degree. Will not update if in automated observation state. 
    Example: 
                        >> settings --longitude -123.28925
    ''')
    parser.add_argument('--elevation', '--height', action='store', nargs=1, metavar='<elevation>',
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
    parser.add_argument('--plate_solve', '-solve', action='store', nargs=1, metavar='<nova.astrometry.net API key>',
                        help ='''\
    Set a nova.astrometry.net API key to use for plate solving. Leaving this blank, or setting it to False, None, or
    0 will skip the plate solving process. Be sure to keep your API key private. You can also use nova.astrometry.net
    to monitor your unit remotely and see some of its most recent images that are being used for plate solving.
    ''')
    parser.add_argument('--abort_after_failure_to_plate_solve', '-solve_abort_behavior', action='store', nargs=1, choices=["True", "False"],
                        help='''\
    Set to False (default) to continue observing after an image has failed to be plate solved. If an image can't be
    plate solved, it is of little to no scientific value. Set to True to have the unit skip to the next target in
    the queue. WORK IN PROGRESS, CURRENTLY NON-FUNCTIONAL, SYSTEM WILL CONTINUE TO OBSERVE AFTER FAILED PLATE SOLVE
    NO MATTER WHAT THIS IS SET TO.
    ''')

    parser.add_argument('--simulators', '-sim', action='store', nargs='+', metavar='<simulator 1> <simulator2> <simulator3>',
                        help='''\
    Set which simulators you would like to use to bypass safety settings. Bypassing these settings is useful for
    testing but is discouraged in an actual deployment. Possible simulator names are: "night", "weather", or "power".
    You may use multiple simulators by typing the name of one, followed by a space, and then another. 
    Example: 
                        >> settings --simulators night weather power
    ''')

    args = parser.parse_args()
    main(args)


    
