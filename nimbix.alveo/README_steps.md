# Vitessedata Deepgreen with MLSuite Installation Guide

## Environment and Requirement
We assume that Xilinx Hardware (Alveo) and MLSuite has been properly
installed.   The following installation steps are tested on nimbix
Xilinx ML Suite Alveo U200 Development Kit. 

Edit env.sh as necessary.

User must be able to sudo.   User must set up ~/.ssh so that he/she
can ssh localhost without password.

Next, run each of the following shell scritps.

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

## 04\_xdrive.sh
Setup xdrive and related stuff.

## 05\_sql.sh
Setup a bunch of SQL scrtips.  You will see a few ERROR: xxx does not exist.  
These are OK.

## Start googlenet server.
```
cd py
. ./conda2.sh
./rungnet.sh
```
These will start a googlnet image classifier on FPGA.  It will run in 
foreground.   You can daemonize it if you want to, but I would just 
let it run and print out stuff to console.

## Run a test
```
. ./deepgreendb/greenplum_path.sh
psql -f sql/gnet.sql 
psql -f sql/gnet2.sql
```
This will run googlenet image classification on some pictures.  Table
imagefiles contains the caltech 101 image dataset that is downloaded 
in 01\_download.sh.   sql/gnet2.sql shows you can apply a SQL predicate
(in the dir panda), the classification result can be put in a subquery 
and then, further processed. 

The following query will run googlenet on all caltech 101 dataset and 
report timing.  
```
psql -f sql/gnetall.sql
```
