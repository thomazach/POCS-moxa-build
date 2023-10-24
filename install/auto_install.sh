#!/bin/bash

echo "                 -------- Auto-Install Statement --------
This script was developed without access to a Raspberry Pi, it is likely that
it may encounter errors while trying to set everything up. It would be 
extremely helpful for users to record or document errors they encounter and
open a github issue at 
https://github.com/thomazach/POCS-moxa-build/tree/develop

Make sure you have a stable internet connection and don't remove power from
the unit while this script is running. You will be prompted for input at 
certain times:
When installing gphoto2 select option 2, stable

                 -------- Starting Auto-Install --------
"

function MoxaInstall {
    echo "Auto-installation is not currently supported on the Moxa devices."
    exit 1

}

function PiInstall {
    echo "                 -------- Installing Required apt Packages --------"
    sudo apt-get update && sudo apt-get upgrade -y
    sudo apt-get install curl dcraw=9.27 python3-pip -y
    sudo mv /usr/lib/python3.11/EXTERNALLY-MANAGED /usr/lib/python3.11/EXTERNALLY-MANAGED.old
    echo "                 -------- Installing Required Python pip Packages --------"
    sudo pip install astropy colorlog pyserial
    echo "                 -------- Installing the arduino-cli --------"
    curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
    echo "                 -------- Installing gphoto2 --------"
    wget https://raw.githubusercontent.com/gonzalo/gphoto2-updater/master/gphoto2-updater.sh && wget https://raw.githubusercontent.com/gonzalo/gphoto2-updater/master/.env && chmod +x gphoto2-updater.sh && sudo ./gphoto2-updater.sh
}

cd ~
# Ask user which processor they are using, Moxa or Raspbian
while true; do
    read -p "What processor are you using: [Moxa/Pi] " user_input

    if [ "$user_input" == "Moxa" ]; then
        MoxaInstall
        break
    elif [ "$user_input" == "Pi" ]; then
        PiInstall
        break
    else
        echo "Invalid input. Please enter 'Moxa' or 'Pi'."
    fi
done

echo "                 -------- Installing moxa-POCS --------"
git clone --branch develop https://github.com/thomazach/POCS-moxa-build.git