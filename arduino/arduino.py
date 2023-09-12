import serial
import time
import pickle
import os
import sys

'''
Arduino expects:
"<command_integer,argument_integer>"
command integers:
    0:
        Turns off a relay specified by argument_integer (0 to 4)
    1: 
        Turns on a relay specified by argument_integer (0 to 4)
    2:
        Arduino measures electrical current values and sends them to serial
        with a start and end marker of "|"
    
Example: <1,1> turns off relay in relayArray[1]

RELAY_0 ---> Weather sensor
RELAY_1 ---> Unassigned
RELAY_2 ---> Fan
RELAY_3 ---> Cameras
RELAY_4 ---> Mount
'''

parentDirectory = os.path.realpath(__file__).replace('/arduino/arduino.py', '')
sys.path.append(parentDirectory)

from user_scripts.schedule import bcolors
from logger.astro_logger import astroLogger

DEFAULT_ARDUINO_PORT = '/dev/ttyACM0'

def serialize_commands(readable_command: str):
    '''
    Converts a readable command (ex. cameras off) to an arduino serial readable command (ex. <0,3>)

    Isn't case sensitive, all inputs are converted to lower case
    Doesn't support command names that have a blank space (" ")
    '''

    logger.debug("Converting human readable command to an arduino serial command.")
    readable_command = readable_command.lower()
    array_cmd = list(filter(None, readable_command.split(" ")))

    on_off_bool = lambda status: 1 if status.lower() == "on" else 0

    match array_cmd[0]: 

        case "cameras" | "mount" | "fan" | "weather" | "unassigned":
            try:
                cmd = on_off_bool(array_cmd[1])
            except IndexError:
                print("The specified command requries arguments. Sending empty command to Arduino.")
                return "".encode("utf-8")
            match array_cmd[0]:
                case "weather":
                    cmd_arg = 0
                case "unassigned":
                    cmd_arg = 1
                    print(bcolors.YELLOW + "\n=WARN= Referenced arduino pin is not attached to hardware." + bcolors.ENDC)
                case "fan":
                    cmd_arg = 2
                case "cameras":
                    cmd_arg = 3
                case "mount":
                    cmd_arg = 4
            logger.debug(f"Arduino serial command: {f'<{cmd},{cmd_arg}>'.encode('utf-8')}")
            return f'<{cmd},{cmd_arg}>'.encode("utf-8")
        
        case "current" | "currents" | "get_current" | "get_currents":
            logger.debug(f"Arduino serial command: {f'<2>'.encode('utf-8')}")
            return f'<2>'.encode("utf-8")
        
        case "read_weather" | "get_weather" | "read_weather_sensor" | "get_weather_sensor":
            logger.debug(f"Arduino serial command: {f'<3>'.encode('utf-8')}")
            return f'<3>'.encode("utf-8")

def listen(port):
    # Function listens for a response from the arduino and returns the requested data or the completion character
    output = str(port.readline().decode('utf-8'))
    output = output.replace("\r", "")
    output = output.replace("\n", "")
    if output.count("|") == 2:
        output = output.replace("|", "")
        if output.__contains__(","):
            csvData = list(filter(None, output.split(',')))
            response = []
            for entry in csvData:
                response.append(int(entry))
            logger.info(f"Recieved the following data requested by the command: {response}")
            return response
        elif output == "#":
            logger.info("Recieved successful command execution character from the Arduino.")
            return bcolors.OKGREEN + "\nExecuted Command Successfully" + bcolors.ENDC
        elif output == "r":
            print(bcolors.OKGREEN + "\nArduino setup complete. Ready for commands." + bcolors.ENDC)
            logger.info("Succesfully connected and initialized the Arduino.")
            return True
        
    elif output.count("|") != 0 and output.count("|") != 2:
        logger.error("Arduino serial communication error. Expected command response within two '|' characters. ")
        return bcolors.YELLOW + 'WARNING: Arduino serial communication error or timeout. Expected command response within two "|" characters.' + bcolors.ENDC
    
    else:
        logger.warn("Unexpected serial response. Possible Arduino serial communication timeout reached.")
        print("Unexpected serial response. Possible Arduino serial communication timeout reached.")
        return None

def main():
    logger.info(f"Attempting to connect to arduino on {DEFAULT_ARDUINO_PORT}")
    with serial.Serial(DEFAULT_ARDUINO_PORT, 9600, timeout=5) as arduinoPort:
        # Can't send serial commands before setup() has completed
        ready = False
        while not ready:
            ready = listen(arduinoPort)

        pickleFilePath = f'{os.path.dirname(os.path.dirname(__file__))}/pickle/arduino_cmd.pickle'
        On = True
        while On:
            with open(pickleFilePath, "rb") as f:
                commandDict = pickle.load(f)
                logger.debug(f"Loaded arduino_cmd.pickle and recieved command dictionary: {commandDict}")

            if commandDict['cmd'].lower() == "off" and commandDict['execute'] == True:
                logger.info(f"Turning off the arduino service.")
                commandDict['execute'] = False
                with open(pickleFilePath, "wb") as f:
                    pickle.dump(commandDict, f)
                On = False
                continue

            if commandDict['execute'] == True:
                logger.info(f"Attempting to execute arduino command: {commandDict['cmd']}")
                arduinoReadyCommand = serialize_commands(commandDict['cmd'])
                # TODO: When logging is added log the command sent to the arduino
                arduinoPort.write(arduinoReadyCommand)
                commandDict['response'] = listen(arduinoPort)

            if commandDict['response'] != "waiting for response":
                commandDict['execute'] = False
                with open(pickleFilePath, "wb") as f:
                    pickle.dump(commandDict, f)
                    logger.debug("Arduino's response has been written to arduino_cmd.pickle.")

            time.sleep(1)

if __name__ == "__main__":
    logger = astroLogger(enable_color=True)
    main()
