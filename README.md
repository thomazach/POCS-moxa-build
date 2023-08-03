# Moxa-POCS
PANOTPES Observatory Control Software for remotely operating a telescope via an ssh connection on a moxa UC-8112A-ME-T series arm processor running moxa industrial linux 1 (MIL1). This repository is designed to be a recode of [POCS](https://github.com/panoptes/POCS) for specific hardware. Main changes include a move away from object oriented programming and server/docker based communication to threading, explicit seperation of hardware for future compatibility, modular software architecture, removal of virtual environments (conda) from production builds, and thorough documentation to support both users and developers.


# For Users:  
Project is incomplete as of updating this document (8/3/2023). The main [POCS](https://github.com/panoptes/POCS) repository designed for the RasPi build in Buhtan is the best version of POCS available to date. Before beginning your build, you should [explore the official panoptes website](projectpanoptes.org), [contact](https://www.projectpanoptes.org/overview/contact) the PANOTPES team, and explore the [forum](forum.projectpanoptes.org).  
## Compatible Hardware  
This repository is hardware specific. It is designed to work with an [iEQ30Pro](https://www.ioptron.com/product-p/3000e.htm) equitorial telescope mount, two [Cannon EOS 100Ds](https://www.canon.com.cy/for_home/product_finder/cameras/digital_slr/eos_100d/), [Arduino Uno Rev3](https://store.arduino.cc/products/arduino-uno-rev3) accompanied by a [power distribution header](https://www.infineon.com/dgdl/Infineon-24V_ProtectedSwitchShield_with_Profet+24V_for_Arduino_UsersManual_10.pdf-UserManual-v01_01-EN.pdf?fileId=5546d46255dd933d0156074933e91fe2), and either a [moxa control computer](https://www.moxa.com/en/products/industrial-computing/arm-based-computers/uc-8100a-me-t-series) or Rasberry Pi. You can find in-depth documentation for this build here. Working with other hardware will likely cause problems, and you will need to develop solutions on your own. This repository is designed such that it can be used as a framework where only portions need to be rewritten for new hardware. For more information, please refer to the section "For Developers".
## Install
(WIP non-functional)  
1. Clone this repository and run the install dependencies script.
2. Upload power_board.ino to the arduino using the arduino-cli (possibly using automatic uploading)
## Operation
The unit is controlled through a custom shell that can be launched by (WIP). Below is a table of shell commands.
|Command|Arguments|Description|
|:---|:---:|---|
|`start_automated_observation`|None|Prompts the user to select a target list and then puts the system into its autonomous observation state to run indefinetly and collect images.|
|`stop_observation`|None|Safely exits the autonomous observation state. If unit is actively tracking targets and taking images, this will park the mount and terminate remaining camera threads after the current image is done being taken.|
|`make_target_list`|None|Starts frontend/prompts user for creating a new `targets.yaml` file.|
|`edit_target_list`|None|Starts frontend/prompts user to choose an existing target list and edit it. Allows for both updating previous targets and adding new ones.|
|`config`|None|Starts frotend/prompts user for location information, official PAN ID|
|`config_usb`|None| (WIP, usb config system not implemented, lower priority) Starts frontend/prompts user to manually enter device paths. Only necessary if there are serial devices other than mount, arduino, and cameras connected (or if their dev paths were taken by previously connected serial hardware).|
|`arduino`|`on`, `off`, `current`, `read_weather`,`cameras`, `mount`, `fan`, `weather`, `unassigned`|Keyword command for interacting with the arduino. Arguments: `on` will call arduino.py and enable control of the arduino using the other commands. `off` will stop arduino.py and leave the arduino running with current relays. (relays will be turned on if `arduino on` is run again)|
|`arduino current`|None|Returns the electrical current flowing through each relay as a 0-1023 integer (Will be updated to be an actual current unit later).|
|`arduino read_weather`|None|Currently non-functional, but will return values from the weather sensor once the arduino weather station is developed.|
|`arduino cameras`|`on`, `off`|Turn the power to the cameras on or off. Wiring based off of [this](https://www.youtube.com/watch?v=Uq_ytlCmLIw) video.|
|`arduino mount`|`on`, `off`|Turn the power to the mount on or off. Wiring based off of [this](https://www.youtube.com/watch?v=Uq_ytlCmLIw) video.|
|`arduino fan`|`on`, `off`|Turn the power to the fan on or off. Wiring based off of [this](https://www.youtube.com/watch?v=Uq_ytlCmLIw) video.|
|`arduino weather`|`on`, `off`|Turn the power to the weather sensor on or off. Wiring based off of [this](https://www.youtube.com/watch?v=Uq_ytlCmLIw) video.|
|`arduino unassigned`|`on`, `off`|Turn the power on or off for the unused pin on the arduino board. Wiring based off of [this](https://www.youtube.com/watch?v=Uq_ytlCmLIw) video.|
# For Developers:  
## Commitment to End Users, Project PANOPTES, & Open Source
As a repository contributing to citizen science, we have special commitments that need to be upheld. This is an open source repository, and pull requests that add barriers to development, are obfuscated, implement mandatory pay walls, or require the user to pay for third party software/dependencies will not be merged. We also have end users with vastly different computer skills. As a developer, it is your responsibility to thoroughly document the features you create with guides and examples. Merges to main (production) will not be accepted without reasonable documentation. Features should be developed based on community and PANOPTES team feedback, either from the weekly meetings or the [PANOPTES forum](forum.projectpanoptes.org).  
TODO:  
Create convention for sharing documentation 


## Pull Requests
(WIP, currently a private repo in early developmnet)
- No pickle files for security reasons

## Modular Software Architecture
The hardware available to builders will change over time, and to accomodate future builds each piece of hardware has its own module and subdirectory. The goal is to enable builders with different hardware to be able to recode only the module(s) they need. Because of this, each hardware module cannot import functions or classes from other hardware modules. However, they can import functions and classes from modules that won't **require** an update to continue functioning. We refer to the modules that won't **require** updates as static modules. A breakdown of static vs hardware modules can be found below.

Static modules:
- observational_scheduler  
- core


Hardware modules:
- arduino
- cameras
- mount
- weather_analysis

### Communication Between Modules
Python's pickle feature is used to communicate between modules. The convention of this repository is to place all pickle files in the **`pickle` subdirectory** with an informative name followed by `.pickle`. The core "module" (which is really just core.py) runs in a loop, writes information (generally target data) to the relevant `.pickle` file and then *usually* runs a python hardware module that will look for that pickle file for instructions. The table below shows the naming conventions of this repositories pickle files. 
|File Name|Purpose|
|:---|:---|
|`current_target.pickle`|Facilitate communication between the mount, cameras, and core. Contains an object with attributes for the current command, RA/DEC position, and image settings.|
|`arduino_cmd.pickle`|(WIP) Used for communicating with the arduino module. Contains an object with a human-readable arduino command, execution state, and response field.|  

A visual representation of autonomous communication flow:

### Overview of Modules
The following overview was made during development, and is subject to change. Is accurate as of 8/3/2023.
#### `core` 
This module runs perpetually during autonomous observation. It is responsible for checking weather conditions, deciding what to observe (based on user preference and moon position), when to observe, and feeding the rest of the system with an individual target via `current_target.pickle`. It will feed the system multiple individual targets throughout the night.
#### `observational_scheduler` 
This module is imported by core. It contains a target class that contains important information about a single star or field. This includes RA/DEC coordinates, image settings, and a command that will be recognized by other modules. It also contains the `getTargetQueue` function, which creates a heap of target instances ordered from highest priority to lowest priority based off of a specified `.yaml` file. This function is called in core to create a list of targets it will attempt to observe.
#### `mount` 
This mount module is designed for the iEQ30Pro. This mount uses the serial [iOptron RS-232 Command Language V2.5](http://www.ioptron.com/v/ASCOM/RS-232_Command_Language2014_V2.5.pdf). The mount module uses this command langauge along with pyserial to control the mount. After core writes a target instance to `current_target.pickle`, it executes the mount module which will then establish communication with the mount, start an ongoing loop and read the pickle file. If the target instance's `cmd` attribute is `'slew to target'` the mount will unpark, slew to the specified coordinates in the pickle file and start tracking. It will then change the pickle files `cmd` attribute to `'take images'` and call the `cameras` module. The mount loop will end and park the mount after the cameras have finished taking images.
#### `cameras` 
The camera module uses the [gphoto2](http://gphoto.org/) command line interface to control the cameras. After it is called by the mount module, it reads the pickle file to make sure that the command is `'take_images'`, at which point it automatically detects the cameras, and takes an "observation," which is several long exposure images on both cameras using multiprocessing. The specifics of the observation are determined by the `camera_settings` attribute in the pickle file. The images are stored to the `images` directory with timestamped directories. Once both multiprocesses have finished, the module sets the `cmd` attribute of the pickle file to `'observation_complete'` and exits. This command signals the mount module to park and core to send the next target to observe.
#### `arduino`
The arduino module uses pyserial to start direct serail communication. The arduino module is run in a permenant loop, since connecting to an arduino with pyserial will restart it, causing the setup() function to run which can cause unwanted behavior. On the python side, the arduino repeatedly checks the `arduino_cmd.pickle` file for new commands from other modules or users in the custom shell. It then processes the entered command into a serial command code (integer), puts appropriate start and end characters, and sends it to the arduino. On the arduino side, it recieves this command, executes it, and returns a success code or the requested data with start and end characters. The response is then written to the pickle file. The pickle file contains a dictionary with specific keys. This is an example of a valid dictionary to read the currents on the arduinos output pins:  
`{'cmd': 'currents', 'execute': True, 'response': 'waiting for response'}`
#### `weather_analysis` Module
The weather station is currently being redesigned, and as such this module is a WIP. The main idea is that it analyzes the results of a connected weather sensor and communicates a True/False statement about weather safety to core.  

## User Input and Configuration Files
We use yaml files to store configuration information. We don't allow users to edit these directly. It is best practice for this project to keep `.yaml` and `.yml` files write locked to the user in production, and allow the user to edit them using a dedicated front end. Developers are responsible for providing documentation for this frontend for users of all skill levels (assuming basic computer knowledge).
## Code Style & Naming Conventions
Taijen fill this out.
