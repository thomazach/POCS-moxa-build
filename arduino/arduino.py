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

cmd = '<1, 0>'
with serial.Serial(DEFAULT_ARDUINO_PORT, 9600) as arduinoPort:
    arduinoPort.write(cmd.encode('utf-8'))
    while True:
            output = arduinoPort.readline().decode("utf-8")
            print(f'From arduino: {output}')
