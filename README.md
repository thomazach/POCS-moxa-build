# Moxa-POCS
PANOTPES Observatory Control Software remotely operates a telescope via an SSH connection on a Moxa UC-8112A-ME-T series arm processor or Raspberry Pi. This repository is designed to be an update of [POCS](https://github.com/panoptes/POCS) that is more compatible with the Moxa processor. Main changes include a move away from object oriented programming and server/docker based communication to threading, explicit separation of hardware modules for future compatibility, modular software architecture, removal of virtual environments (conda) from production builds, and thorough documentation to support both users and developers.

# Key Features
- Front End for All Settings
- Scriptable CLI
- Modular Software Architecture
- Documentation for End Users and Developers

# For Users:  
Before beginning your build, you should [explore the official panoptes website](projectpanoptes.org), [contact](https://www.projectpanoptes.org/overview/contact) the PANOTPES team, and explore the [forum](forum.projectpanoptes.org). **The v1.0.0 release is missing three planned features:** weather sensing, detection and handling of power loss, and tracking correction.  
## Compatible Hardware  
This repository is hardware specific. It is designed to work with an [iEQ30Pro](https://www.ioptron.com/product-p/3000e.htm) equitorial telescope mount, two [Cannon EOS 100Ds](https://www.canon.com.cy/for_home/product_finder/cameras/digital_slr/eos_100d/), [Arduino Uno Rev3](https://store.arduino.cc/products/arduino-uno-rev3) accompanied by a [power distribution header](https://www.infineon.com/dgdl/Infineon-24V_ProtectedSwitchShield_with_Profet+24V_for_Arduino_UsersManual_10.pdf-UserManual-v01_01-EN.pdf?fileId=5546d46255dd933d0156074933e91fe2), and either a [moxa control computer](https://www.moxa.com/en/products/industrial-computing/arm-based-computers/uc-8100a-me-t-series) or Raspberry Pi. You can find in-depth documentation for this build here. Working with other hardware will likely cause problems, and you will need to develop solutions on your own. This repository is designed such that it can be used as a framework where only portions need to be rewritten for new hardware. For more information, please refer to the section "For Developers".
## Install
On Raspberry Pi Unbuntu Server:
```
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt install python3-pip
$ sudo mv /usr/lib/python3.11/EXTERNALLY-MANAGED /usr/lib/python3.11/EXTERNALLY-MANAGED.old
$ sudo pip install astropy   # sudo required otherwise it will try to make a user installation
$ sudo pip install colorlog  # sudo required otherwise it will try to make a user installation
### Choose 2 (stable version) after running the command below ###
$ wget https://raw.githubusercontent.com/gonzalo/gphoto2-updater/master/gphoto2-updater.sh && wget https://raw.githubusercontent.com/gonzalo/gphoto2-updater/master/.env && chmod +x gphoto2-updater.sh && sudo ./gphoto2-updater.sh

$ git clone https://github.com/thomazach/POCS-moxa-build.git
```
On a Moxa processor running Moxa Industrial Linux 1 (MIL1): (This section is still a work in progress.)
```
sudo nano /etc/network/interfaces.d
```
Replace the two occurences of `static` with `dhcp`, save and exit the file.
```
sudo reboot
# Verify that internet is working with ping:
ping www.google.com  # Should recieve bytes, note that networks that redirect to login pages will recieve bytes but won't allow proper functioning of the internet
sudo nano /etc/apt/sources.list
# Make the contents of the file be:
deb mirror://debian.moxa.com/debian/mirrors stretch main

deb http://archive.debian.org/debian/ stretch main contrib non-free
#deb-src http://deb.debian.org/debian stretch main contrib non-free

deb http://archive.debian.org/debian-security/ stretch/updates main contrib non-free
#deb-src http://security.debian.org/ stretch/updates main contrib non-free
### Save and exit the file ###
sudo apt-get update     # Accept all prompts
sudo apt-get upgrade    # Accept all prompts
sudo apt install git

git clone https://github.com/thomazach/POCS-moxa-build.git
```
Work in progress: Installing dependenicies on Moxa device  
### Quick Start  
After a succesful installation:
1. Start the `panoptes-CLI` shell with: `python3 ~/POCS-moxa-build/panoptes-CLI.py`
2. Use the `settings` command to set the location of your unit.
3. Use the `schedule` command to create a schedule file and select it as the active schedule file.
4. Use the `start` command to put the unit into an automated observation state  
## Operation
The unit is controlled through a custom shell that can be launched from a terminal with `python3 ~/POCS-moxa-build/panoptes-CLI.py`. Below is a table of available shell commands. Please note that the shell's built-in help documentation includes shortcuts not listed here, and may be in a more accessible format.
|Command|Arguments|Description|
|:---|:-----:|---|
|`help` |None|Displays the base commands of the panoptes-CLI. Bases can be run with -h or --help as arguments to get further usage information.|
|`start`|`--force`|Puts the system into its autonomous observation state to run indefinetly and collect images. Requires settings to be configured and targets specified in a schedule file. The `--force` or `-f` argument reset the systems stored on/off states to off. This argument is useful for recovering after an unhandled error.|
|`stop`|None|Safely exits the autonomous observation state. If unit is actively tracking targets and taking images, this will attempt to gracefully exit.|
|`schedule`|`--show_active_observation`, `--list_target_files`, `--select <name>.yaml`, `--new <name>.yaml`, `--edit <name>.yaml`, `--delete <name>.yaml` |Interact with the schedule system and specify targets to observe. The `--show_active_observation` or `-show` argument displays the name of the currently selected schedule file, the targets it contains, and prompts the user to view more detailed information about each target. The `--list_target_files` or `-ls` argument will list the names of available schedule files that the unit can use. The `--select` or `-s` argument sets the current schedule file to the one specified after `--select` (ex: `>> schedule --select test_fields.yaml`). The `--new` or `-n` argument allows the user to specify the name of a new schedule file that will be created and then prompts the user for target information. The `--edit` or `-e` argument lets the user edit the specified schedule file interactively. The `--delete` or `-rm` argument deletes the schedulefile specified by the user.|
|`settings`|`--show`,`--latitude <float>`, `--longitude <float>`, `--elevation <float>`, `-set_log` |Edit system settings, including location and displayed logging level. The `--show` argument displays the current settings. The `--latitude` followed by a number sets the latitude. The `--longitude` argument followed by a number sets the longitude. The `--elevation` argument followed by a number sets the elevation above sea level in meters. The `-set_log` argument followed by `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` sets the lowest displayed logging level.|
|`arduino`|`on`, `off`, `current`, `read_weather`,`cameras`, `mount`, `fan`, `weather`, `unassigned`|Keyword command for interacting with the arduino. Arguments: `on` will call arduino.py and enable control of the arduino using the other commands. `off` will stop arduino.py and leave the arduino running with current relays. (relays will be turned on if `arduino on` is run again)|
|`arduino current`|None|Returns the electrical current flowing through each relay as a 0-1023 integer (Will be updated to be an actual current unit later).|
|`arduino read_weather`|None|Currently non-functional, but will return values from the weather sensor once the arduino weather station is developed.|
|`arduino cameras`|`on`, `off`|Turn the power to the cameras on or off. Wiring based off of [this](https://www.youtube.com/watch?v=Uq_ytlCmLIw) video.|
|`arduino mount`|`on`, `off`|Turn the power to the mount on or off. Wiring based off of [this](https://www.youtube.com/watch?v=Uq_ytlCmLIw) video.|
|`arduino fan`|`on`, `off`|Turn the power to the fan on or off. Wiring based off of [this](https://www.youtube.com/watch?v=Uq_ytlCmLIw) video.|
|`arduino weather`|`on`, `off`|Turn the power to the weather sensor on or off. Wiring based off of [this](https://www.youtube.com/watch?v=Uq_ytlCmLIw) video.|
|`arduino unassigned`|`on`, `off`|Turn the power on or off for the unused pin on the arduino board. Wiring based off of [this](https://www.youtube.com/watch?v=Uq_ytlCmLIw) video.|
## Advanced Operation  
The panoptes-CLI documented in the "Operation" section is a simple shell that calls executable python files in the `user_scripts` directory. Using the CLI is **not** required to control a panoptes unit running moxa-pocs. For example, running `~/user_scripts/schedule.py --select test_fields.yaml` on the command line has the same effect as running `schedule --select test_fields.yaml` in the panoptes-CLI. This is easily extended to third party and end user automation. By calling the executables in `user_scripts` from another file, you can achieve functionality that isn't provided directly. For example, consider this standalone python script that will observe normally, and then at a specific time automatically switch to observing a different schedule file:
```python
import os
import threading
import time

from datetime import datetime

# The 'start' CLI command is blocking, and needs to threaded to allow following lines to execute
def nonBlockingStart():
    os.system('~/POCS-moxa-build/user_scripts/start.py')

startThread = threading.Thread(target=nonBlockingStart)
startThread.start()

# Create a permenant loop that will run until a specific date and time
while True:

    # At a specific time down to the minute:
    val  = datetime.now().strftime("%d/%m/%Y %H:%M")
    if val == "31/08/2023 16:57":

        # stop automated observation
        os.system('~/POCS-moxa-build/user_scripts/stop.py')

        # Switch to a pre-made schedule file with a single target
        os.system('~/POCS-moxa-build/user_scripts/schedule.py --select exoplanet_transit_at_4AM.yaml')
        os.system('~/POCS-moxa-build/user_scripts/start.py')
        break

    time.sleep(20)
### NOT TESTED ON HARDWARE, use at your own risk
```
**Automated scripts like this will not work well with commands that require user input.** If an advanced user creates a script that is truly helpful, it can be added to the `user_scripts` folder and integrated with the panoptes-CLI to give users even more CLI commands and tools.  
# For Developers:  
## Commitment to End Users, Project PANOPTES, & Open Source
As a repository contributing to citizen science, we have special commitments that need to be upheld. This is an open source repository, and pull requests that add barriers to development, are obfuscated, implement pay walls, or require the user to pay for third party software/dependencies will not be merged. We also have end users with vastly different computer skills. As a developer, it is your responsibility to thoroughly document the features you create with guides and examples. Merges to main (production) will not be accepted without reasonable documentation. Features should be developed based on community and PANOPTES team feedback, either from the weekly meetings or the [PANOPTES forum](forum.projectpanoptes.org).  

## Pull Requests
All pull requests should be made on the develop branch. If the pull request is approved by a maintainer and is merged to develop, the develop branch must be tested on hardware successfully for a duration of three days before it can be merged to main. In the future, the three day test will need to include successful detection and response to both weather conditions and power conditions. Additionally, **do not include your system's pickle or yaml files** in your pull requests. You may include third party wrappers as explained in the Advanced Operation section, but they must be placed within the `user_scripts` directory and be refactored to be compatible with the `panoptes-CLI`.

## Modular Software Architecture
The hardware available to builders will change over time, and to accomodate future builds each piece of hardware has its own module and subdirectory. The goal is to enable builders with different hardware to be able to recode only the module(s) they need. Because of this, each hardware module cannot import functions or classes from other hardware modules. However, they can import functions and classes from modules that won't **require** an update to continue functioning. We refer to the modules that won't **require** updates as static modules. A breakdown of static vs hardware modules can be found below.

Static modules:
- core
- observational_scheduler  
- logger


Hardware modules:
- arduino
- cameras
- mount
- weather_analysis  
  
As long as these modules communicate uniformly and achieve their high-level purpose, they can be replaced/updated by users with different hardware without effecting the rest of the system.

### Communication Between Modules
Python's pickle feature is used to communicate between modules. The convention of this repository is to place all pickle files in the **`pickle` subdirectory** with an informative name followed by `.pickle`. The core module runs in a loop, writes information (generally target data) to the relevant `.pickle` file and then *usually* runs a python hardware module that will look for that pickle file for instructions. The table below shows the naming conventions of this repositories pickle files. 
|File Name|Purpose|
|:---|:---|
|`current_target.pickle`|Facilitate communication between the mount, cameras, and core. Contains an object with attributes for the current command, RA/DEC position, and image settings.|
|`arduino_cmd.pickle`| Used for communicating with the arduino module. Contains an object with a human-readable arduino command, execution state, and response field.|  
|`system_info.pickle` | Stores the desired on/off state of the system along with the actual on/off state. Used for graceful exiting during observation and in the future will be used to hold ASCOM telescope states and relevant non-constant system wide information.|

A visual representation of information flow and module calls:
![Moxa-POCS Flowchart](https://github.com/thomazach/POCS-moxa-build/assets/86134403/ba5f3c14-efb5-46c4-8457-624bf11e5a43)

### Overview of Modules
The following overview was made during development, and is subject to change. Is accurate as of 9/10/2023.
#### `core` 
This module runs continually during autonomous observation. It is responsible for checking safety conditions, observation conditions, deciding what to observe (based on user preference and moon position), and feeding the rest of the system with targets to observe via `current_target.pickle`. 
#### `observational_scheduler` 
This module is imported by core. It contains a target class that has important information about a single star or field. This includes RA/DEC coordinates, image settings, and a command that will be recognized by other modules. It also contains the `getTargetQueue` function, which creates a heap of target instances ordered from highest priority to lowest priority based off of a specified `.yaml` file. This function is called in core to create a list of targets that the system will attempt to observe.
#### `logger`
This module is the system wide logging object, called `astroLogger`. It supports colored logs and inherits python's `logging.Logger` object, and is used in the same way. When initializing the logger, please use `logger = astroLogger(color_enabled=True)` for consistency. Log files are located in `/logger/logs/`, and each python file is given its own log file.
#### `mount` 
This mount module is designed for the iEQ30Pro. This mount uses the serial [iOptron RS-232 Command Language V2.5](http://www.ioptron.com/v/ASCOM/RS-232_Command_Language2014_V2.5.pdf). The mount module uses this command language along with pyserial to control the mount. After core writes a target instance to `current_target.pickle`, it executes the mount module which will then establish communication with the mount, start an ongoing loop and read the pickle file. If the target instance's `cmd` attribute is `'slew to target'` the mount will unpark, slew to the specified coordinates in the pickle file and start tracking. It will then change the pickle files `cmd` attribute to `'take images'` and call the `cameras` module. The mount loop will end and park the mount after the cameras have finished taking images.
#### `cameras` 
The camera module uses the [gphoto2](http://gphoto.org/) command line interface to control the cameras. After it is called by the mount module, it reads the pickle file to make sure that the command is `'take images'`, at which point it automatically detects the cameras, and takes an "observation," which is several long exposure images on both cameras using multiprocessing. The specifics of the observation are determined by the `camera_settings` attribute in the pickle file. The images are stored to the `images` directory with timestamped directories. Once both multiprocesses have finished, the module sets the `cmd` attribute of the pickle file to `'observation complete'` and exits. This command signals the mount module to park, and once parked the mount module issues a command that tells core to send the next target to observe.
#### `arduino`
The arduino module uses pyserial for direct serial communication. The arduino module is run in a permanant loop, since connecting to an arduino with pyserial will restart it, causing the setup() function to run which can cause unwanted behavior. On the python side, the arduino module repeatedly checks the `arduino_cmd.pickle` file for new commands from other modules or users in the custom shell. It then processes the entered command into a serial command code (integer), puts appropriate start and end characters, and sends the command to the arduino. On the arduino side, the arduino recieves this command, executes it, and returns a success code or the requested data with start and end characters. The response is then written to the pickle file. The pickle file contains a dictionary with specific keys. This is an example of a valid dictionary to read the currents on the arduinos output pins:  
`{'cmd': 'currents', 'execute': True, 'response': 'waiting for response'}`
#### `weather_analysis`
The weather station is currently being redesigned, and as such this module is a work-in-progress. The main concept is that the module will analyze the results of a connected weather sensor and communicate a True or False statement about weather safety to core. This statement is currently forced to be true in the `core` module for the time being.

## User Input and Configuration Files
We use yaml files to store configuration information. We don't allow users to edit these directly. It is best practice for this project to keep `.yaml` hidden from the user in production, and allow the user to edit them using a dedicated front end. Developers are responsible for providing documentation for users of all skill levels (assuming basic computer knowledge).
