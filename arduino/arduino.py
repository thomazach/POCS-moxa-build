import serial
import time
<<<<<<< HEAD
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
    output = port.readline().decode('utf-8')
    print(output)

cmd = getTestSerialCommands()

with serial.Serial(DEFAULT_ARDUINO_PORT, 9600, timeout=5) as arduinoPort:
    time.sleep(5)
    arduinoPort.write(cmd)
    time.sleep(2)
    listen(arduinoPort)
    while True:
            listen(arduinoPort)
            time.sleep(1)
            cmd = getTestSerialCommands()
            arduinoPort.write(cmd)
=======

DEFAULT_ARDUINO_PORT = '/dev/ttyACM0'

def getTestSerialCommands():
    pin_num = input("Enter pin number:")
    state = input("Enter on or off:")
    value = f"{pin_num},{state}".encode("utf-8")
    return bytes(value)

while True:

    cmd = getTestSerialCommands()

    with serial.Serial(DEFAULT_ARDUINO_PORT, 9600) as arduinoPort:
        arduinoPort.write(cmd)
        time.sleep(3)
        output = arduinoPort.readline()
        print(f"From arduino: {output}")

<<<<<<< HEAD
>>>>>>> 073a191 (Initial arduino infrastructure, going to test on dev unit)
=======
>>>>>>> 416731f (Initial arduino infrastructure, going to test on dev unit)
>>>>>>> 862fc7c (Initial arduino infrastructure, going to test on dev unit)
