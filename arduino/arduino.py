import serial
import time

DEFAULT_ARDUINO_PORT = '/dev/ttyACM0'


def getTestSerialCommands():
    command = input(">>")
    value = bytes(f'<{command}>', 'utf-8')
    return value

# 
cmd = getTestSerialCommands()

with serial.Serial(DEFAULT_ARDUINO_PORT, 9600, timeout=5) as arduinoPort:
    arduinoPort.write(cmd)
    while True:
            output = arduinoPort.readline()
            print(output)
