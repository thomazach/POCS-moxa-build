import pickle
import time

while True:
    _ = input(">>")
    arduino_command = {'cmd': _, 'execute': True, 'response': "waiting for response"}
    with open('/home/WISRD/POCS-moxa-build/pickle/arduino_cmd.pickle', 'wb') as f:
        pickle.dump(arduino_command, f)
    time.sleep(3)
    with open('/home/WISRD/POCS-moxa-build/pickle/arduino_cmd.pickle', 'rb') as f:
        cmd = pickle.load(f)
    print(cmd['response'])
