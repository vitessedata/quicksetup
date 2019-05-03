#!/bin/bash

set -e
set -x

apt update
apt install -y tmux
apt install -y python-opencv
apt install -y python-protobuf
apt install -y python-pip

sudo rm /bin/sh
sudo ln -s /bin/bash /bin/sh

cat ./config/sysctl.conf.add >> /etc/sysctl.conf 
cat ./config/limits.conf.add >> /etc/security/limits.conf 

