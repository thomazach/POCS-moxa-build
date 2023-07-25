import serial
import time

DEFAULT_ARDUINO_PORT = '/dev/ttyACM0'


def getTestSerialCommands():
    command = input(">>")
    value = f'<{command}>'
    return value.encode("utf-8")

cmd = getTestSerialCommands()
print(cmd)

with serial.Serial(DEFAULT_ARDUINO_PORT, 9600, timeout=5) as arduinoPort:
    time.sleep(5)
    arduinoPort.write(cmd)
    while True:
            output = arduinoPort.readline()
            print(output)
