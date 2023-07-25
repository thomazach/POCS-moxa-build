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

cmd = "<1>"
with serial.Serial(DEFAULT_ARDUINO_PORT, 9600, timeout=1, rtscts=True) as arduinoPort:
    arduinoPort.write(bytes(cmd, 'utf-8'))
    while True:
            time.sleep(1)
            output = arduinoPort.readline().decode("utf-8")
            print(output)
