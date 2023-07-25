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
with serial.Serial(DEFAULT_ARDUINO_PORT, 9600, timeout=1, rtscts=True) as arduinoPort:
    arduinoPort.write(cmd)
    while True:
            time.sleep(1)
            output = arduinoPort.readline().decode("utf-8")
            arduinoPort.write(cmd)
            print(output)
