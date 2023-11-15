# Moxa-POCS
PANOTPES Observatory Control Software remotely operates a telescope via an SSH connection on a Moxa UC-8112A-ME-T series arm processor or Raspberry Pi. This repository is designed to be an update of [POCS](https://github.com/panoptes/POCS) that is more compatible with the Moxa processor. Main changes include a move away from object oriented programming and server/docker based communication to threading, explicit separation of hardware modules for future compatibility, modular software architecture, removal of virtual environments (conda) from production builds, and thorough documentation to support both users and developers. Moxa-POCS is designed to be a framework for building, developing, and distributing hardware and software solutions.

# Key Features
- Front End for All Settings
- Documentation for End Users and Developers
- Modular Software Architecture
- Package System for Third Party Development & Distribution
- Scriptable CLI
# Table of Contents
- [Moxa-POCS Introduction](#moxa-pocs)
- [Key Features](#key-features)
- [User Guide](#for-users)
    - [Compatible Hardware](#compatible-hardware)
    - [Install](#install)
    - [Quick Start](#quick-start)
    - [Operation](#operation)
    - [Packages](#packages)
    - [Advanced Operation](#advanced-operation)
- [Developer Guide](#for-developers)
    - [Commitment to End Users, Project PANOPTES, & Open Source](#commitment-to-end-users-project-panoptes--open-source)
    - [Pull Requests](#pull-requests)
    - [Modular Software Architecture](#modular-software-architecture)
        - [Communication Between Modules](#communication-between-modules)
        - [Overview of Modules](#overview-of-modules)
             - [`core`](#core)
             - [`observational_scheduler`](#observational_scheduler)
             - [`logger`](#logger)
             - [`mount`](#mount)
             - [`cameras`](#cameras)
             - [`arduino`](#arduino)
             - [`weather_analysis`](#weather_analysis)
    - [User Input and Configuration Files](#user-input-and-configuration-files)
    - [Developing Packages](#developing-packages)

# For Users:  
Before beginning your build, you should [explore the official panoptes website](projectpanoptes.org), [contact](https://www.projectpanoptes.org/overview/contact) the PANOTPES team, and explore the [forum](forum.projectpanoptes.org). **The v1.0.0 release is missing two planned features:** weather sensing and handling of sudden power loss.
## Compatible Hardware  
Moxa-POCS only offers "out of the box" functionality for a single build. Currently, it is designed to work with a [CEM40]([https://www.ioptron.com/product-p/3000e.htm](https://www.ioptron.com/product-p/c401a1.htm)) equitorial telescope mount, two [Cannon EOS 100Ds](https://www.canon.com.cy/for_home/product_finder/cameras/digital_slr/eos_100d/), [Arduino Uno Rev3](https://store.arduino.cc/products/arduino-uno-rev3) accompanied by a [power distribution header](https://www.infineon.com/dgdl/Infineon-24V_ProtectedSwitchShield_with_Profet+24V_for_Arduino_UsersManual_10.pdf-UserManual-v01_01-EN.pdf?fileId=5546d46255dd933d0156074933e91fe2), and either a [moxa control computer](https://www.moxa.com/en/products/industrial-computing/arm-based-computers/uc-8100a-me-t-series) or Raspberry Pi. You can find in-depth documentation for this build here(WIP). Moxa-POCS can also support the [iEQ30Pro](https://www.ioptron.com/product-p/3000e.htm) mount, however a package will need to be installed after downloading the baseline software. Using other hardware will likely cause problems, and you will need to develop solutions on your own.
## Install
On Raspberry Pi Unbuntu Server, run this command to begin an automatic installation:
```
cd ~; wget https://raw.githubusercontent.com/thomazach/POCS-moxa-build/develop/install/auto_install.sh; bash ~/auto_install.sh
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
2. Use the `package` shell command to remove old hardware software and install new software (see the packages section for more information).
3. Use the `settings` shell command to set the location of your unit.
4. Use the `schedule` shell command to create a schedule file and select it as the active schedule file.
5. Use the `start` shell command to put the unit into an automated observation state  
  
As an optional step that will improve your unit's performance, you can enable plate solving by:
1. Visiting [nova.astrometry.net](nova.astrometry.net) and logging in/creating an account
2. Going to your Dashboard --> My Profile
3. Finding your API key (the green text in the "Account Info" box) 
4. Using the `settings --plate_solve <API key from step 3>` command to enter your API key
As an added bonus, you can also use astrometry.net's Dashboard --> My Images tab to see some of the images your unit is taking in real time.  
## Operation
The unit is controlled through a custom shell that can be launched from a terminal with `python3 ~/POCS-moxa-build/panoptes-CLI.py`. Below is a table of available shell commands. Please note that the shell's built-in help documentation includes shortcuts not listed here, and may be in a more accessible format.
|Command|Arguments|Description|
|:---|:-----:|---|
|`help` |None|Displays the commands available to the panoptes-CLI, including commands added by packages. The listed commands can be run with -h or --help as arguments to get further usage information.|
|`start`|`--force`|Puts the system into its autonomous observation state to run indefinetly and collect images. Requires settings to be configured and targets specified in a schedule file. The `--force` or `-f` argument reset the systems stored on/off states to off. This argument is useful for recovering after an unhandled error.|
|`stop`|None|Safely exits the autonomous observation state. If unit is actively tracking targets and taking images, this will attempt to gracefully exit.|
|`schedule`|`--show_active_observation`, `--list_target_files`, `--select <name>.yaml`, `--new <name>.yaml`, `--edit <name>.yaml`, `--delete <name>.yaml` |Interact with the schedule system and specify targets to observe. The `--show_active_observation` or `-show` argument displays the name of the currently selected schedule file, the targets it contains, and prompts the user to view more detailed information about each target. The `--list_target_files` or `-ls` argument will list the names of available schedule files that the unit can use. The `--select` or `-s` argument sets the current schedule file to the one specified after `--select` (ex: `>> schedule --select test_fields.yaml`). The `--new` or `-n` argument allows the user to specify the name of a new schedule file that will be created and then prompts the user for target information. The `--edit` or `-e` argument lets the user edit the specified schedule file interactively. The `--delete` or `-rm` argument deletes the schedulefile specified by the user.|
|`settings`|`--show`,`--latitude <float>`, `--longitude <float>`, `--elevation <float>`, `-set_log` |Edit system settings, including location and displayed logging level. The `--show` argument displays the current settings. The `--latitude` followed by a number sets the latitude. The `--longitude` argument followed by a number sets the longitude. The `--elevation` argument followed by a number sets the elevation above sea level in meters. The `-set_log` argument followed by `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` sets the lowest displayed logging level.|
|`package`|`--install`, `--remove`, `--update`, `--show`, `--install_from_directory`|Manage standard packages by installing, removing, and updating them. After an argument, specify the package name (this is not case sensitive). Note that the `--update` argument removes and reinstalls the package, which will delete stored settings. The `--show` argument will list the names of currently installed packages. The `--install` and `--update` arguments can be passed an additionaly `--install_from_directory` argument which will attempt to install the contents of the specified directory (ex: `>> package --install custom_package_name --install_from_directory /path/to/package/directory`). When `--install_from_directory` is run with `--install`, the package name specified after `--install` can be anything, and will have no effect on what is installed, but will be the name used to manage future removal and updating of the package. When updating a package that was installed from a directory, the `--install_from_directory` argument must be specified and the supplied path should be an updated directory of the same package.|
|`arduino`|`on`, `off`, `current`, `read_weather`,`cameras`, `mount`, `fan`, `weather`, `unassigned`|Keyword command for interacting with the arduino. Arguments: `on` will call arduino.py and enable control of the arduino using the other commands. `off` will stop arduino.py and leave the arduino running with current relays. (relays will be turned on if `arduino on` is run again)|
|`arduino current`|None|Returns the electrical current flowing through each relay as a 0-1023 integer (Will be updated to be an actual current unit later).|
|`arduino read_weather`|None|Currently non-functional, but will return values from the weather sensor once the arduino weather station is developed.|
|`arduino cameras`|`on`, `off`|Turn the power to the cameras on or off. Wiring based off of [this](https://www.youtube.com/watch?v=Uq_ytlCmLIw) video.|
|`arduino mount`|`on`, `off`|Turn the power to the mount on or off. Wiring based off of [this](https://www.youtube.com/watch?v=Uq_ytlCmLIw) video.|
|`arduino fan`|`on`, `off`|Turn the power to the fan on or off. Wiring based off of [this](https://www.youtube.com/watch?v=Uq_ytlCmLIw) video.|
|`arduino weather`|`on`, `off`|Turn the power to the weather sensor on or off. Wiring based off of [this](https://www.youtube.com/watch?v=Uq_ytlCmLIw) video.|
|`arduino unassigned`|`on`, `off`|Turn the power on or off for the unused pin on the arduino board. Wiring based off of [this](https://www.youtube.com/watch?v=Uq_ytlCmLIw) video.|
## Packages  
Moxa-POCS supports the development and installation of third-party packages. Packages are designed to add features and customization options not present in default PANOPTES builds, and may require additional hardware. You can install standard and non-standard PANOPTES packages through the panoptes-CLI. For standard packages, simply use `>> package --install <package name>`, for non-standard packages, you will need to specify the directory(outside of `~/POCS-moxa-build`) containing the package. This can be done with the `-from_dir` argument. For example:  
`>> package --install <desired name of package> -from_dir </path/to/package>`  
This is a table of standard Moxa-POCS packages that can be easily downloaded using the CLI.  
|`panoptes-CLI` Name|Description|Link|Developer|  
|:---:|:---|:---:|:---:|  
|CEM40|This moxa-pocs package is designed for the CEM40 German equatorial telescope mount. It should work with a wide range of mounts listed in iOptron's RS-232 Serial Command Language V3.10. Updates are planned for manual, scriptable mount control.|[Github](https://github.com/thomazach/Moxa-POCS-Fundamental-Packages/tree/CEM40)| thomazach |  
|iEQ30Pro|This moxa-pocs package is designed for the iEQ30Pro German equatorial telescope mount. It should work with a wide range of mounts listed in iOptron's RS-232 Serial Command Language V2.5.|[Github](https://github.com/thomazach/Moxa-POCS-Fundamental-Packages/tree/IEQ30Pro)| thomazach |  
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
As a repository contributing to citizen science, we have special commitments that need to be upheld. This is an open source repository, and pull requests that add barriers to development, are obfuscated, implement pay walls, or require the user to pay for third party software/dependencies will not be merged. We also have end users with vastly different computer skills. As a developer, it is your responsibility to thoroughly document the features you create with guides and examples. Documentation should be sufficient to support high school students with little to no computer knowledge. Merges to main (production) will not be accepted without reasonable documentation. Features should be developed based on community and PANOPTES team feedback, either from the weekly meetings or the [PANOPTES forum](forum.projectpanoptes.org).  

## Pull Requests
All pull requests for non-package code should be made on the develop branch. If the pull request is approved by a maintainer and is merged to develop, the develop branch must be tested on hardware successfully for a duration of three days before it can be merged to main. In the future, the three day test will need to include successful detection and response to both weather conditions and power conditions. Additionally, **do not include your system's pickle or yaml files** in your pull requests. You may include third party wrappers as explained in the Advanced Operation section, but they must be placed within the `user_scripts` directory and be refactored to be compatible with the `panoptes-CLI`. If you have improvements to add to a package, open a pull request on that package's github. If the package effects the baseline build, once your changes have been merged in the package's github and made into a release, you may open a pull request here with the updated changes to get github contribution.

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
  
As long as these modules communicate uniformly and achieve their high-level purpose, they can be replaced/updated by users with different hardware without effecting the rest of the system. Developers who create their own custom solutions are encouraged to turn their code into a package, so that it can be distributed to all Moxa-POCS users. For more information on how to do this, see the [Developing Packages](#developing-packages) section.

### Communication Between Modules
Python's pickle feature is used to communicate between modules. The convention of this repository is to place all pickle files in the **`pickle` subdirectory** with an informative name followed by `.pickle`. The core module runs in a loop, writes information (generally target data) to the relevant `.pickle` file and then *usually* runs a python hardware module that will look for that pickle file for instructions. The table below shows the naming conventions of this repositories pickle files. 
|File Name|Purpose|
|:---|:---|
|`current_target.pickle`|Facilitate communication between the mount, cameras, and core. Contains an object with attributes for the current command, RA/DEC position, and image settings.|
|`arduino_cmd.pickle`| Used for communicating with the arduino module. Contains an object with a human-readable arduino command, execution state, and response field.|  
|`system_info.pickle` | Stores the desired on/off state of the system along with the actual on/off state. Used for graceful exiting during observation and in the future will be used to hold ASCOM telescope states and relevant non-constant system wide information.|

A visual representation of information flow and module calls:
![Moxa-POCS Flowchart](https://github.com/thomazach/POCS-moxa-build/assets/86134403/3d84d89c-ac93-4dc5-a8a7-66e3e108b99d)


### Overview of Modules
The following overview was made during development, and is subject to change. Is accurate as of 9/10/2023.
#### `core` 
This module runs continually during autonomous observation. It is responsible for checking safety conditions, observation conditions, deciding what to observe (based on user preference and moon position), and feeding the rest of the system with targets to observe via `current_target.pickle`. 
#### `observational_scheduler` 
This module is imported by core. It contains a target class that has important information about a single star or field. This includes RA/DEC coordinates, image settings, and a command that will be recognized by other modules. It also contains the `getTargetQueue` function, which creates a heap of target instances ordered from highest priority to lowest priority based off of a specified `.yaml` file. This function is called in core to create a list of targets that the system will attempt to observe.
#### `logger`
This module is the system wide logging object, called `astroLogger`. It supports colored logs and inherits python's `logging.Logger` object, and is used in the same way. When initializing the logger, please use `logger = astroLogger(color_enabled=True)` for consistency. Log files are located in `/logger/logs/`, and each python file is given its own log file.
#### `mount` 
This mount module is designed for the [CEM40](https://www.ioptron.com/product-p/c401a1.htm). This mount uses the serial [iOptron RS-232 Command Language V3.10](https://www.ioptron.com/v/ASCOM/RS-232_Command_Language2014V310.pdf). The mount module uses this command language along with pyserial to control the mount. After core writes a target instance to `current_target.pickle`, it executes the mount module which will then establish communication with the mount, start an ongoing loop and read the pickle file. If the target instance's `cmd` attribute is `'slew to target'` the mount will unpark, go to the home position, slew to the specified coordinates in the pickle file, and start tracking. It will then change the pickle files `cmd` attribute to `'take images'` and call the `cameras` module. If the specific mount module/package has tracking correction or guiding set up, this module will also plate solve result images and perform corrections accordingly. The mount loop will end and park the mount after the cameras have finished taking images.
#### `cameras` 
The camera module uses the [gphoto2](http://gphoto.org/) command line interface to control the cameras. After it is called by the mount module, it reads the pickle file to make sure that the command is `'take images'`, at which point it automatically detects the cameras, and takes an "observation," which is several long exposure images on both cameras using multiprocessing. The specifics of the observation are determined by the `camera_settings` attribute in the pickle file. The images are stored to the `images` directory with timestamped directories. Once both multiprocesses have finished, the module sets the `cmd` attribute of the pickle file to `'observation complete'` and exits. This command signals the mount module to park, and once parked the mount module issues a command that tells core to send the next target to observe.
#### `arduino`
The arduino module uses pyserial for direct serial communication. The arduino module is run in a permanant loop, since connecting to an arduino with pyserial will restart it, causing the setup() function to run which can cause unwanted behavior. On the python side, the arduino module repeatedly checks the `arduino_cmd.pickle` file for new commands from other modules or users in the custom shell. It then processes the entered command into a serial command code (integer), puts appropriate start and end characters, and sends the command to the arduino. On the arduino side, the arduino recieves this command, executes it, and returns a success code or the requested data with start and end characters. The response is then written to the pickle file. The pickle file contains a dictionary with specific keys. This is an example of a valid dictionary to read the currents on the arduinos output pins:  
`{'cmd': 'currents', 'execute': True, 'response': 'waiting for response'}`
#### `weather_analysis`
The weather station is currently being redesigned, and as such this module is a work-in-progress. The main concept is that the module will analyze the results of a connected weather sensor and communicate a True or False statement about weather safety to core. This statement is currently forced to be true in the `core` module for the time being.

## User Input and Configuration Files
We use yaml files to store configuration information. We don't allow users to edit these directly. It is best practice for this project to keep `.yaml` hidden from the user in production, and allow the user to edit them using a dedicated front end. Developers are responsible for providing documentation for users of all skill levels (assuming basic computer knowledge).  
## Developing Packages
The `package` command in the panoptes-CLI gives developers a way to add additional functionality and customization to units, and then distribute these upgrades to users. The `>>package --install <standard package name>` command searches for `<standard package name>` in a match and case statement, where each case runs the standard package's custom installation instructions. Generally, this installs any required dependencies, downloads a package's source code to a temporary directory, copies and pastes the contents of the temporary folder into `~/POCS-moxa-build`, and finally deletes the temporary folder. To create your own custom package, create a github repository with the source code of the package located in `packages/name-of-your-package`, and CLI integration in `user_scripts/panoptes_CLI_compatible_command.py` (note that the CLI supports any language as long as it is executable as a script with a proper shebang). This is the suggested format so that your package's files and commands can be easily located by the user. Currently, there are two standard packages that are desigend to support two different mounts, the CEM40 and iEQ30Pro. Both are hosted on the same [github page](https://github.com/thomazach/Moxa-POCS-Fundamental-Packages), and are a good example of how packages can be used to support different kinds of hardware. Additionally, the panoptes3D project is currently under development, and [this branch](https://github.com/sarumanplaysguitar/panoptes3D/tree/moxa-pocs-panoptes3d-pkg) is being organized into a standard PANOPTES package that will provide additional visualization functionality to units as opposed to just adding compatibility with different hardware. To become a standard package you can open a pull request on the develop branch that modifies the `install` function in `user_scripts/package.py` with custom installation instructions that:  
  
1. Are matched to your package name
2. Download your tar ball from your github release
3. Unzip the tar ball to `~/your-repo-name` and delete the old tar ball
4. Install any relevant dependencies on both the Raspbian and Moxa builds
5. package.py will then copy and paste the package's file structure into `POCS-moxa-build` and record the locations of installed files
6. package.py will then delete the temporary directory containing the standard package
  
To update a standard package, you will need to make another pull request for your package that changes the link of the older release to that of the newer one. **You must make this pull request using the same github account.** In order **for your pull request to be merged**, your package must:  
  
1. Provide new functionality and/or features
2. Be integrated with the `panoptes-CLI` by placing commands in `user_scripts/your-executable-command-here` and handle all user input exclusively through the `panoptes-CLI`
3. Integrated commands should support the development of light weight wrappers, as explained in the [Advanced Operation section](#advanced-operation)
4. Integrated commands must have a `-h` or `--help` argument that explains how to use them.
5. If the package is written in python, it should use this project's logging object, explained [here](#logger). If it is written in a different language, logs should be placed in `logger/logs/package_logs/package_name`.
6. If required, package settings should be placed in `conf_files/package-name-settings.yaml`
7. Be documented and in accordance with [Commitment to End Users, Project PANOPTES, & Open Source](#commitment-to-end-users-project-panoptes--open-source)

**If your package universally improves source code for all users, and there are no reasons why some users wouldn't want the features, we would perfer to merge your package directly to source code.**  
