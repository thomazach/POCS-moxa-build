#!/usr/bin/python3

def main():
    print("---------------   Available PANOPTES commands   ---------------")
    print(bcolors.OKCYAN + "arduino" + bcolors.ENDC)
    print(bcolors.OKCYAN + "schedule" + bcolors.ENDC)
    print(bcolors.OKCYAN + "settings" + bcolors.ENDC)
    print("USAGE:")
    print('''\
Add a "-h" argument to the end of a command to get detailed information about its arguments.
Example:
            >> schedule -h
          ''')

if __name__ == "__main__":
    from schedule import bcolors
    main()