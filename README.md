# POCS-moxa-build
PANOTPES Observatory Control Software for remotely operating a telescope via an ssh connection on a moxa UC-8100A-ME-T series arm processor running moxa industrial linux. This repository is designed to be a refactor and upgrade to [POCS](https://github.com/panoptes/POCS). Main changes include a move away from server/docker based communication to read/write lock threading, explicit seperation of "non-core" threads
for future compatibility, removal of virtual environments (conda) from production builds, and thorough documentation to support both users and developers.  

# For Users:  
Project is incomplete. The main [POCS](https://github.com/panoptes/POCS) repository designed for the RasPi build in Buhtan is the best version of POCS available to date. Before beginning your build, you should [explore the official panoptes website](projectpanoptes.org), [contact](https://www.projectpanoptes.org/overview/contact) the PANOTPES team, and explore the [forum](forum.projectpanoptes.org).

# For Developers:  
A more in depth outline of the initial plan can be found below:

![moxa-pocs-initial-outline](https://github.com/thomazach/POCS-moxa-build/assets/86134403/d4b77057-8be9-44f1-b0b5-29fd411166c0)
[View](https://miro.com/welcomeonboard/emVlejZRR25IZkVBSUYzaGFZR2FBYW05enV1d3owRVVEMTYxVTZ5QnM4OHVJZDcwU3JDTEpGQ3VxeVV0ZHlTQ3wzNDU4NzY0NTU3ODAzNzg3MDc1fDI=?share_link_id=458349056185) this projects Miro whiteboard. (Screenshotted above as of 6/22/23)

Many of the things this repository seeks to do have already been done at [panoptes/POCS](github.com/panoptes/POCS), and the code will likely rely on a lot of ideas from that repo. Like [POCS](https://github.com/panoptes/POCS), this repository will be written mainly in python. For interested developers, please review [astropy](https://www.astropy.org/), mount [control command language](http://www.ioptron.com/v/ASCOM/RS-232_Command_Language2014V310.pdf), the [gphoto2 library](http://www.gphoto.org/) which will be used to control two Cannon EOS [2000D](https://www.canon-europe.com/support/consumer_products/products/cameras/digital_slr/eos-2000d.html?type=drivers&language=en&os=windows%2010%20(64-bit))/[Rebel T7](https://www.usa.canon.com/support/p/eos-rebel-t7), the main [weather sensor](https://shop.lunaticoastro.com/?product=aag-cloudwatcher-cloud-detector), its [software](https://indilib.org/devices/weather-stations/aag-cloud-watcher.html) and our [moxa control computer](https://www.moxa.com/en/products/industrial-computing/arm-based-computers/uc-8100a-me-t-series). 

Please reach out before starting/contributing to development.
Email: thomazac@oregonstate.edu  
Panoptes Forum: @"Zach"#p174
