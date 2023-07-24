import serial
import time

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

