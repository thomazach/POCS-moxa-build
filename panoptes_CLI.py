import os
import threading

from user_scripts.schedule import bcolors

# TODO: Add color output and logging

PARENT_DIRECTORY = os.path.dirname(__file__)

def execBlocking(cmdString):
    os.system(cmdString)

def execThreaded(cmdString):
    return threading.Thread(target=execBlocking, args=[cmdString]).start()

class command:
    def __init__(self, userInput):
        try:
            parts = userInput.split()
        except Exception as error:
            print('=ERROR= ', error)

        cmd = parts[0]
        realFile = None
        for file in os.listdir(f'{PARENT_DIRECTORY}/user_scripts'):
            if file.split('.')[0] == cmd:
                realFile = file
                break

        
        cmdString = f"{PARENT_DIRECTORY}/user_scripts/{realFile} {userInput.replace(cmd, '')}"

        doThreading = False
        if (cmd == 'arduino') and ('--listen' in userInput or '-on' in userInput):
            doThreading = True
        if cmd == 'start':
            doThreading = True


        if doThreading:
            execThreaded(cmdString)
        else:
            execBlocking(cmdString)

        

def _betterInput(prompt, Type = str, default = None):
    #TODO: Implement the mountCommand class so that I can also have it 
    #      handled here

    result = None
    while result == None:
        userInput = input(prompt) or default
        if userInput:
            try:
                result = Type(userInput)
            except TypeError as error:
                print('=INVALID= Your input was not of type ', Type, 'with error:', error)
                userInput = None
            except Exception as error:
                print('=ERROR= ', error)
                userInput = None
    return result

def main():

    while True:
        cmd = _betterInput(">> ", command, None)

if __name__ == '__main__':
    main()