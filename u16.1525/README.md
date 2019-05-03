# Install Guide Deepgreen 18 and Xilinx ML-Suite On Premise

## OS and Drivers
CPU must be `x86_64` with AVX.  
OS should be Ubuntu 1604 LTS
FPGA is 1525, dsa is `xilinx_vcu1525_dynamic_5_1`

User shell should be bash.  Using csh will definitely not work.
To make sure we start with a clean environment, we recommend 
you to create a new user.  Run the following steps as root/sudo.
```
sudo bash ./user.sh
```

It will create a user deepgreen, password deepGr33n, with sudo 
capability.

Next, login as deepgreen or su deepgreen.  The following document
assumes you have a clean user profile.

## Get this repo.
```
git clone https://github.com/vitessedata/quicksetup
cd quicksetup/u16.1525
```

## Run 00_root.sh
This file need to run as root/sudo
```
sudo bash ./00_root.sh
```

This script will update OS, install tmux, and update /bin/sh to use /bin/bash.   
Ubuntu 16 by default will symlink /bin/sh to /bin/dash. Vitessedata Deepgreen 
requires bash. 


