#!usr/bin/python3

def main(args):
    
    parentDir = os.path.realpath(__file__).replace('/user_scripts/arduino.py', '')

    def writeRead(cmd):
        with open(f"{parentDir}/pickle/arduino_cmd.pickle", "wb") as f:
            pickle.dump(cmd, f)
        time.sleep(2.1)
        with open(f"{parentDir}/pickle/arduino_cmd.pickle", "rb") as f:
            cmdDict = pickle.load(f)
            if cmdDict['response'] != "waiting for response":
                print(cmdDict['response'])
            elif cmdDict['execute'] == True:
                print(bcolors.FAIL +"=ERROR= Did not recieve response from arduino before timeout" + bcolors.ENDC)

    if args.listen:
        try:
            os.system(f"python {parentDir}/arduino/arduino.py")
        except Exception as error:
            print(bcolors.FAIL + "=ERROR=", error)
            print(bcolors.ENDC, end='')

    if args.off:
        cmd = {'cmd': "off", 'execute': True, 'response': "waiting for response"}
        writeRead(cmd)
        print(bcolors.OKGREEN + "Arduino listener shut down." + bcolors.OKGREEN)
    
    if args.read_weather:
        print(bcolors.YELLOW + "=WARN= read_weather hasn't been implemented yet." + bcolors.ENDC)
    
    if args.cameras:
        cmd = {'cmd': f"cameras {args.cameras}", 'execute': True, 'response': "waiting for response"}
        writeRead(cmd)
    
    if args.mount:
        cmd = {'cmd': f"mount {args.mount}", 'execute': True, 'response': "waiting for response"}
        writeRead(cmd)
    
    if args.fan:
        cmd = {'cmd': f"fan {args.fan}", 'execute': True, 'response': "waiting for response"}
        writeRead(cmd)

    if args.weather_station:
        cmd = {'cmd': f"weather {args.weather_station}", 'execute': True, 'response': "waiting for response"}
        writeRead(cmd)
    
    if args.unassigned:
        cmd = {'cmd': f"unassigned {args.unassigned}", 'execute': True, 'response': "waiting for response"}
        writeRead(cmd)

    if args.current:
        cmd = {'cmd': f"current", 'execute': True, 'response': "waiting for response"}
        writeRead(cmd)

if __name__ == "__main__":
    import argparse
    import os 
    import pickle
    import time

    from schedule import bcolors

    parser = argparse.ArgumentParser(description="Control the arduino.", formatter_class=argparse.RawTextHelpFormatter)
    arduino_cmds = parser.add_mutually_exclusive_group()

    arduino_cmds.add_argument('-on', '--listen', required=False, action='store_true', help='''\
Call the arduino module's listener, connecting to the arduino, running void_setup() in power_board.ino, and enabling control of the arduino using the other commands.
                              
''')
    arduino_cmds.add_argument('--off', '-f', required=False, action='store_true', help='''\
Stop the arduino module's listener and leave the arduino running with current relays. (relays will be turned on if "arduino on" is run again)
                              
''')
    arduino_cmds.add_argument('--read_weather', required=False, action='store_true', help='''\
NOT CURRENTLY IMPLEMENTED. Read the weather sensor and print sensor values and system determined weather state.
                              
''')
    arduino_cmds.add_argument('--cameras', '--camera', '-cam', '-cams', required=False, action='store', choices=['on', 'off'], metavar='on/off', help='''\
Turn the power to the cameras on or off. Wiring based off of:
https://www.youtube.com/watch?v=Uq_ytlCmLIw
                              
''')
    arduino_cmds.add_argument('--mount', required=False, action='store', choices=['on', 'off'], metavar='on/off', help='''\
Turn the power to the mount on or off. Wiring based off of:
https://www.youtube.com/watch?v=Uq_ytlCmLIw
                              
''')
    arduino_cmds.add_argument('--fan', required=False, action='store', choices=['on', 'off'], metavar='on/off', help='''\
Turn the power to the fan on or off. Wiring based off of:
https://www.youtube.com/watch?v=Uq_ytlCmLIw
                              
''')
    arduino_cmds.add_argument('-weather', '--weather_station', required=False, action='store', choices=['on', 'off'], metavar='on/off', help='''\
Turn the power to the weather station on or off. Wiring based off of:
https://www.youtube.com/watch?v=Uq_ytlCmLIw
                              
''')
    arduino_cmds.add_argument('--unassigned', required=False, action='store', choices=['on', 'off'], metavar='on/off', help='''\
Turn the power to the unassigned power relay on or off. Wiring based off of:
https://www.youtube.com/watch?v=Uq_ytlCmLIw
                              
''')
    arduino_cmds.add_argument('--current', '-c', required=False, action='store_true', help='''\
Measure the current on each arduino relay and print the results.
                              
''')

    args = parser.parse_args()
    main(args)