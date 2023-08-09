import serial
import time
import threading

readyForCommand = True

def mount_listen(port):
    message = []
    newResponse = False
    while True:
        char = port.read()
        if char != b'' and newResponse == False:
            newResponse = True

        if newResponse == True and char != b'':
            message.append(char)
        elif char == b'':
            newResponse = False
            print(message)
            message = []
            readyForCommand = True

cmd = 0

with serial.Serial('/dev/ttyUSB0', 9600, timeout=0.1) as mount_port:
    print(mount_port)

    threading.Thread(target=mount_listen, args=[mount_port]).start()

    while True:
        if readyForCommand == True:
            match cmd:
                case 0:
                    mount_port.write(b':MountInfo#')
                    readyForCommand = False
                case 1:
                    mount_port.write(b':FW2#')
                    readyForCommand = False
            
            readyForCommand += 1



