# POCS-moxa-build
PANOTPES Observatory Control Software for a telescope build using a moxa UC-8100 series arm processor.

Designed to be a refactor and upgrade to https://github.com/panoptes/POCS. Main changes include a move away from server/docker based communication to read/write lock threading, explicit seperation of "non-core" threads
for future compatibility, removal of virtual environments (conda) from production builds, and thorough documentation to support both users and developers. A more in depth outline of the initial plan can be found below:

![moxa-pocs-initial-outline](https://github.com/thomazach/POCS-moxa-build/assets/86134403/d4b77057-8be9-44f1-b0b5-29fd411166c0)
Miro whiteboard for above screenshot can be found at:
https://miro.com/welcomeonboard/emVlejZRR25IZkVBSUYzaGFZR2FBYW05enV1d3owRVVEMTYxVTZ5QnM4OHVJZDcwU3JDTEpGQ3VxeVV0ZHlTQ3wzNDU4NzY0NTU3ODAzNzg3MDc1fDI=?share_link_id=458349056185

Many of the things this repository seeks to do have already been done at github.com/panoptes/POCS, and the code will likely rely on a lot of ideas from that repo.
