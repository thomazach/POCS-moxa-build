import serial
import time
import threading

DEFAULT_ARDUINO_PORT = '/dev/ttyACM0'

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


def getTestSerialCommands():
    command = input(">>")
    value = f'<{command}>'
    return value.encode("utf-8")

def listen(port):
     while True:
        output = port.readline().decode('utf-8')
        print(output)

cmd = getTestSerialCommands()

with serial.Serial(DEFAULT_ARDUINO_PORT, 9600, timeout=5) as arduinoPort:
    threading.Thread(target=listen, args=[arduinoPort])
    time.sleep(5)
    arduinoPort.write(cmd)
    while True:
            time.sleep(5)
            cmd = getTestSerialCommands()
            arduinoPort.write(cmd)

