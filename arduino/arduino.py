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
    if command != '':
        value = f'<{command}>'
        return value.encode("utf-8")
    else:
        getTestSerialCommands()

def listen(port):
    i = 0
    while i < 2:
        output = port.readline().decode('utf-8')
        print(output)
        i = i + 1

cmd = getTestSerialCommands()

with serial.Serial(DEFAULT_ARDUINO_PORT, 9600, timeout=5) as arduinoPort:
    time.sleep(5)
    arduinoPort.write(cmd)
    while True:
            listen(arduinoPort)
            time.sleep(1)
            cmd = getTestSerialCommands()
            arduinoPort.write(cmd)
