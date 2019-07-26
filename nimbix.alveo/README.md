# Vitessedata Deepgreen with MLSuite Installation Guide

## Environment and Requirement
The following installation steps are tested on nimbix Xilinx ML Suite Alveo U200 Development Kit. Bootup the nimbix VM. 

## Install
Open an terminal.  While we can install everthing in $HOME, it is 
cleaner to create a directory to hold all the data.   I used $HOME/v.
Run the following command to install everything.
```
mkdir v
cd v
wget -O - https://raw.githubusercontent.com/vitessedata/quicksetup/master/nimbix.alveo/install.sh | bash
```

## Start googlenet server.
ML Suite use a different python environment.  Start *another* terminal.
```
cd ~/v/quicksetup-master/nimbix.alveo/py
. ./conda2.sh
./rungnet.sh
```

## Start jupyter notebook demo
In your original terminal (not the one to start googlenet).
```
cd ~/v/quicksetup-master/nimbix.alveo/nb
jupyter notebook
```
