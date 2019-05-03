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

## 01\_download.sh
Download deepgreen binary and golang 1.9.5, install some python module.
It also downloads some test images.
```
bash ./01_download.sh
```

## 02\_install.sh
Deepgreen software installation.
```
bash ./02_install.sh
```

## 02.5 ssh keys
If you have not setup ssh keys, you should do it now.  You can run the 
following command.  BE CAREFUL: this will over-write your existing ssh keys.  
```
source deepgreendb/greenplum_path.sh
gpssh-exkeys -f ./hostfile
```

## 03\_initdb.sh
Initialize a deepgreen database instance.  Hit [y].
After this step, you have a running database.   We have create database nimbix.
Verify that you can connect to the database.
```
source deepgreendb/greenplum_path.sh
psql
```

## 04\_xdrive.sh
Setup xdrive and related stuff.

## 05\_sql.sh
Setup a bunch of SQL scrtips.  You will see a few ERROR: xxx does not exist.  
These are OK.

