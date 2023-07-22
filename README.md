# POCS: Moxa Build
PANOTPES Observatory Control Software for remotely operating a telescope via an ssh connection on a moxa UC-8112A-ME-T series arm processor running moxa industrial linux. Support is also planned for RasPi setups, in particular the 2023 Buhtan setup.

# For Users:  
This project is incomplete as of updating this document (7/20/2023). The main [POCS](https://github.com/panoptes/POCS) repository designed for the RasPi build in Buhtan is the best version of POCS currently available. Before beginning your build, you should [explore the official panoptes website](projectpanoptes.org), [contact](https://www.projectpanoptes.org/overview/contact) the PANOTPES team, and explore the [forum](forum.projectpanoptes.org). The developers of this repository will not help with troubleshooting before the first release.  

This repository is hardware specific. It is designed to work with an [iEQ30Pro](https://www.ioptron.com/product-p/3000e.htm) equitorial telescope mount, two [Cannon EOS 100Ds](https://www.canon.com.cy/for_home/product_finder/cameras/digital_slr/eos_100d/), [Arduino Uno Rev3](https://store.arduino.cc/products/arduino-uno-rev3) accompanied by a power distribution header, and either a [moxa control computer](https://www.moxa.com/en/products/industrial-computing/arm-based-computers/uc-8100a-me-t-series) or Rasberry Pi. You can find in-depth documentation for this build here. Working with other hardware will likely cause problems, and you will need to develop solutions on your own. This repository is designed such that it can be used as a framework where only portions need to be rewritten for new hardware. For more information, please refer to the section "For Developers".


# For Developers:  
Please reach out before starting/contributing to development.  
### Commitment to End Users, Project PANOPTES, & Open Source
As a repository contributing to citizen science, we have end users with vastly different computer skills. As a developer, it is your responsibility to thoroughly document the features you create with guides and examples. Merges to main (production) will not be accepted without reasonable documentation. Features should be developed based on community and PANOPTES team feedback, either from the weekly meetings or the [PANOPTES forum](forum.projectpanoptes.org). This is an open source repository, and pull requests that add barriers to development, are obfuscated, implement mandatory pay walls, or require the user to pay for third party software/dependencies will not be merged.  
TODO:  
Create convention for sharing documentation  
### Pull Request Policies  
Coming soon, currently this is a private project.  
### Modular Software Framework 
This repository is broken into modules so that it can accomodate future builds with different hardware. Each piece of hardware has its own subdirectory and must not import or inherent anything from other directories. We do allow directories to communicate and call eachother. We consider these hardware directories to be non-static, as we expect them to change and be updated. We consider the astronomy logic portions of the software to be static, in that we expect infrequent, minor updates only. These are the directories we consider static and non-static:

  | Static | Non-Static |
  |:--------:|:------------:|
  |core|mount|
  |obs_scheduler|camera|
  ||weather_sensor|

If you are interested in contributing to hardware modules in non-static directories, please review the mount [control command language](http://www.ioptron.com/v/ASCOM/RS-232_Command_Language2014_V2.5.pdf), the [gphoto2 library](http://www.gphoto.org/) which will be used to control two Cannon EOS [100D](https://www.canon-europe.com/support/consumer_products/products/cameras/digital_slr/eos-2000d.html?type=drivers&language=en&os=windows%2010%20(64-bit)) OR two Cannon EOS [Rebel T7](https://www.usa.canon.com/support/p/eos-rebel-t7), the main [weather sensor](https://shop.lunaticoastro.com/?product=aag-cloudwatcher-cloud-detector), its [software](https://indilib.org/devices/weather-stations/aag-cloud-watcher.html) and our [moxa control computer](https://www.moxa.com/en/products/industrial-computing/arm-based-computers/uc-8100a-me-t-series). When designing non-static hardware modules, be sure that the communication between directories stays the same. 
### Communication Between Modules
This is a diagram showing the communication between directories:  
In most cases, we use pickle to pass objects between processes. At the end of a system cycle (ex. resting during the day) there should be no lingering pickle files. For security reasons, we will not accept pull requests that have pickle files in them.  

### User Input and Configuration Files  
We use yaml files to store configuration information. We don't allow users to edit these directly. It is best practice for this project to keep .yaml and .yml files write locked to the user in production, and allow the user to edit them using a dedicated front end. Developers are responsible for providing documentation for this frontend for users of all skill levels (assuming basic computer knowledge).  
### Code Style and Conventions  
Taijen, fill this out. 
### Developer Contact Information
At this stage of development, please reach out before starting/contributing to development.  
Email: thomazac@oregonstate.edu  
Panoptes Forum: @"Zach"#p174  
