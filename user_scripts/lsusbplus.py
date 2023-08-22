#!/usr/bin/python3
from subprocess import Popen, PIPE

"""

Utility script that lists out usb serial information and the corresponding serial port path,
useful for setting up path configuration files on first setup.

"""
### Old code, could be updated for readability

BASEDIR = 'cd /sys/bus/pci/devices/0000:01:00.0'
DataStorageMatrix = []
TemporaryDataStorageList = []

# Finding dev path and relating it to bus number and dev number
StartLocationProbe = BASEDIR + ' ; find -maxdepth 2 -name "usb*"'
StartLocation = Popen(
    StartLocationProbe,
    shell=True,
    bufsize=64,
    stdin=PIPE,
    stdout=PIPE,
    close_fds=True).stdout.read().strip().decode('utf-8').split('\n')
NumStartLocation = len(StartLocation)
x = NumStartLocation
while x > 0:
    StartLocationIndex = NumStartLocation - x
    NEWBASEDIR = BASEDIR + ' ; cd ' + StartLocation[StartLocationIndex]
    SearchLocationProbe = NEWBASEDIR + ' ; find . -name "*-*:*"'
    SearchLocations = Popen(
        SearchLocationProbe,
        shell=True,
        bufsize=64,
        stdin=PIPE,
        stdout=PIPE,
        close_fds=True).stdout.read().strip().decode('utf-8').split('\n')
    Num_Searches = len(SearchLocations)
    i = Num_Searches
    while i > 0:
        CurrentIndex = Num_Searches - i
        SearchLocation = NEWBASEDIR + ' ; cd ' + SearchLocations[CurrentIndex]
        DevPathProbe = SearchLocation + ' ; find -maxdepth 2 ! -name "tty"  -name "tty*"'
        DEVPATH = Popen(
            DevPathProbe,
            shell=True,
            bufsize=64,
            stdin=PIPE,
            stdout=PIPE,
            close_fds=True).stdout.read().strip().decode('utf-8')
        if (DEVPATH == ""):
            i -= 1
            continue
        if (DEVPATH.startswith("./tty/")):
            PARSEDDEVPATH = DEVPATH.split("./tty/")
            PARSEDDEVPATH.remove("")
        if (DEVPATH != ""):
            if (DEVPATH.startswith("./tty/")):
                PARSEDDEVPATH = DEVPATH.split("./tty/")
            elif (DEVPATH.startswith("./tty")):
                PARSEDDEVPATH = DEVPATH.split("./")
        PARSEDDEVPATH.remove("")
        BUSNUMDEVNUMPROBE = SearchLocation + ' ; cd .. ; echo -n "Bus: " ; cat busnum ; echo -n " Device: " ; cat devnum ; echo -n " ID " ; cat idVendor ; echo -n ":" ; cat idProduct ; echo -n " " ; cat manufacturer ; echo -n ", " ; cat product'
        BUSNUMDEVNUM = Popen(
            BUSNUMDEVNUMPROBE,
            shell=True,
            bufsize=64,
            stdin=PIPE,
            stdout=PIPE,
            close_fds=True).stdout.read().strip().decode('utf-8')
        TemporaryDataStorageList = BUSNUMDEVNUM.split("\n")
        TemporaryDataStorageList.insert(0, PARSEDDEVPATH[0])
        TemporaryDataStorageList.insert(1, " ")
        TemporaryDataStorageList.insert(0, "Dev path: \033[1;32;40m/dev/")
        TemporaryDataStorageList.insert(2, "\033[1;37;40m")
        DataStorageMatrix.append(TemporaryDataStorageList)
        i -= 1
    x -= 1

# Print out that parsed info!
for x in DataStorageMatrix:
    print("")
    for y in x:
        print(y, end='')
print("")