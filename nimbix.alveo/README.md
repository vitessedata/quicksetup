# Vitessedata Deepgreen with MLSuite Installation Guide

## Environment and Requirement
We assume that Xilinx Hardware (Alveo) and MLSuite has been properly
installed.   The following installation steps are tested on nimbix
Xilinx ML Suite Alveo U200 Development Kit. 

Edit env.sh as necessary.

User must be able to sudo.  We install software to typical locations.
Database and data are stored in $DATADIR, default to $DIR/data, and can
be changed in env.sh.  User must create this dir and have write permission.

## 00\_setup.sh
First run this, it basically update OS, install tmux, and update /bin/sh
to use /bin/bash.   Ubuntu 16 by default will symlink /bin/sh to /bin/dash.
Vitessedata Deepgreen requires bash. 

## 01\_download.sh
Download deepgreen binary and golang 1.9.5

## 02\_install.sh
Install golang to /usr/local/go and install deepgreen v18 to $HOME/deepgreendb
Hit a few [ENTER] to accept vitessedata license.

## 03\_initdb.sh
Initialize a deepgreen database instance.  Hit [y].
After this step, you have a running database.   We have create database nimbix.
Verify that you can connect to the database.
```
source deepgreendb/greenplum_path.sh
psql
```


