#!/bin/bash 

set -e 
set -x

# install necessary python stuff.
sudo apt update
sudo apt install -y tmux
# sudo apt install -y python-opencv
# sudo apt install -y python-protobuf 
# sudo apt install -y python-pip
# sudo pip install --upgrade pip
# sudo pip install --upgrade protobuf
# sudo pip install face_recognition

# /bin/sh was symlinked to /bin/dash in ubuntu, not good.
sudo rm /bin/sh
sudo ln -s /bin/bash /bin/sh

