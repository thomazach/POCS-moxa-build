import serial
import time
import pickle
import os

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
DEFAULT_ARDUINO_PORT = '/dev/ttyACM0'

class arduino_command():
    '''
    Object that gets pickled for arduino communication. 
    
    When modules need to exectue an arduino command they must do it through this pickle object, since directly connecting to the arduino's serial 
    port using pyserial will restart the arduino sketch, causing setup() to be run which will change the power states of the pins. This defaults
    to turning everything on. We need this default state for automatic system recovery, but if a user wants the system to run with power off on 
    certain pieces of hardware, everytime a module used an arduino command directly with pyserial the power to that hardware would be turned on again.
    '''
    def __init__(self, cmd, execute = True) -> None:
        self.cmd = cmd
        self.execute = execute
        self.response = "waiting for response"

def serialize_commands(readable_command: str):
    '''
    Converts a readable command (ex. cameras off) to an arduino serial readable command (ex. <0,3>)

    Isn't case sensitive, all inputs are converted to lower case
    Doesn't support command names that have a blank space (" ")
    '''
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
                    raise Warning("Referenced arduino pin is not attached to hardware")
                case "fan":
                    cmd_arg = 2
                case "cameras":
                    cmd_arg = 3
                case "mount":
                    cmd_arg = 4
            return f'<{cmd},{cmd_arg}>'.encode("utf-8")
        
        case "current" | "currents" | "get_current" | "get_currents":
            return f'<2>'.encode("utf-8")
        
        case "weather" | "read_weather" | "get_weather" | "weather_sensor" | "read_weather_sensor" | "get_weather_sensor":
            return f'<3>'.encode("utf-8")

def listen(port):
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
            return response
        elif output == "#":
            return "Executed Command Successfully"
        elif output == "r":
            print("Arduino setup complete. Ready for commands.")
            return True
        
    elif output.count("|") != 2:
        print('WARNING: Arduino serial communication error. Expected command response within two "|" characters.')
    
    else:
        print("Unexpected serial response. Possible Arduino serial communication timeout reached.")
        return None

def main():
    with serial.Serial(DEFAULT_ARDUINO_PORT, 9600, timeout=5) as arduinoPort:
        # Can't send serial commands before setup() has completed
        ready = False
        while not ready:
            ready = listen(arduinoPort)

        pickleFilePath = f'{os.path.dirname(os.path.dirname(__file__))}/pickle/arduino_cmd.pickle'
        On = True
        while On:
            with open(pickleFilePath, "rb") as f:
                commandObject = pickle.load(f)

            if commandObject.cmd.lower() == "off":
                On = False
                continue

            if commandObject.execute == True:
                arduinoReadyCommand = serialize_commands(commandObject.cmd)
                # TODO: When logging is added log the command sent to the arduino
                arduinoPort.write(arduinoReadyCommand)
                commandObject.response = listen(arduinoPort)

            if commandObject.response != "waiting for response":
                commandObject.execute = False
                with open(pickleFilePath, "wb") as f:
                    pickle.dump(commandObject, f)

            time.sleep(1)

if __name__ == "__main__":
    main()
