import serial
import time

DEFAULT_ARDUINO_PORT = '/dev/ttyACM0'

'''
def getTestSerialCommands():
    pin_num = input("Enter pin number:")
    state = input("Enter on or off:")
    value = f"{pin_num},{state}"
    return value

cmd = getTestSerialCommands()
'''

cmd = b'<off, 1><give_temps>'
with serial.Serial(DEFAULT_ARDUINO_PORT, 9600, rtscts=True) as arduinoPort:
    arduinoPort.write(cmd)
    while True:
            output = arduinoPort.readline().decode("utf-8")
            arduinoPort.write(cmd)
