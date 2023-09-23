#!/usr/bin/python3

def main():

    thisDir = os.path.dirname(__file__)

    cmdRaw = os.popen(f'ls {thisDir}').read()
    files = cmdRaw.split('\n')

    print("---------------   Available PANOPTES commands   ---------------")

    for file in files:
        if ("." in file) and (file != "help.py"):
            print(bcolors.OKCYAN + file[0:file.find(".")] + bcolors.ENDC)

    print("USAGE:")
    print('''\
Add a "-h" argument to the end of a command to get detailed information about its arguments.
Example:
            >> schedule -h
          ''')

if __name__ == "__main__":

    import os

    from schedule import bcolors

    main()
