#!/bin/sh
# Installer for alarm clock

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

echo 'Setting up for alarm clock'
apt-get update
apt-get -y install python-serial
mkdir /home/pi/master/log

echo 'Configure system files'
cp startclock.service /lib/systemd/system
chmod 644 /lib/systemd/system/startclock.service
systemctl daemon-reload
systemctl enable startclock.service