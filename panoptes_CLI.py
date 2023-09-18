import os
import threading

from user_scripts.schedule import bcolors
from logger.astro_logger import astroLogger

PARENT_DIRECTORY = os.path.dirname(__file__)

def execBlocking(cmdString):
    logger.debug(f"Executing blocking command: {cmdString}")
    os.system(cmdString)

def execThreaded(cmdString):
    logger.debug(f"Executing threaded command: {cmdString}")
    return threading.Thread(target=execBlocking, args=[cmdString]).start()

class command:
    def __init__(self, userInput):
        try:
            parts = userInput.split()
        except Exception as error:
            logger.critical(f"Error parsing command: {userInput} With error: {error}")
            print('=ERROR= ', error)

        cmd = parts[0]
        realFile = None
        for file in os.listdir(f'{PARENT_DIRECTORY}/user_scripts'):
            if file.split('.')[0] == cmd:
                realFile = file
                logger.debug(f"Found the {cmd} command in user_scripts")
                break

        cmdString = f"{PARENT_DIRECTORY}/user_scripts/{realFile} {userInput.replace(cmd, '', 1)}"

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

    result = None
    while result == None:
        userInput = input(prompt) or default
        if userInput:
            logger.debug(f">> {userInput}")
            try:
                result = Type(userInput)
            except TypeError as error:
                print('=INVALID= Your input was not of type ', Type, 'with error:', error)
                logger.warning(f"User entered command had a type error. {error}")
                userInput = None
            except Exception as error:
                print('=ERROR= ', error)
                logger.critical(error)
                userInput = None
    return result

def main():

    while True:
        cmd = _betterInput(">> ", command, None)

if __name__ == '__main__':
    logger = astroLogger(enable_color=True)
    main()