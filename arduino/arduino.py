import serial
import time

DEFAULT_ARDUINO_PORT = '/dev/ttyACM0'


def getTestSerialCommands():
    command = input(">>")
    value = f'<{command}>'
    return value

cmd = getTestSerialCommands()

with serial.Serial(DEFAULT_ARDUINO_PORT, 9600, timeout=5) as arduinoPort:
    arduinoPort.write(bytes(cmd, "utf-8"))
    while True:
            output = arduinoPort.readline()
            print(output)
