# Install Guide Deepgreen 18 and Xilinx ML-Suite On Premise

## OS and Drivers
CPU must be `x86_64` with AVX.  
OS should be Ubuntu 1604 LTS
FPGA is 1525, dsa is `xilinx_vcu1525_dynamic_5_1`

edit 
User shell should be bash.  Using csh will definitely not work.
To make sure we start with a clean environment, we recommend 
you to create a new user.  Run the following steps as root/sudo.
```
sudo bash ./user.sh
```

It will create a user deepgreen, password deepGr33n, with sudo 
capability.

If you did not create new user but want to use an existing user,
you may need to check RemoveIPC is set to no.   
```
# edit /etc/systemd/logind.conf
RemoveIPC=no

# restart systemd-logind
service systemd-logind restart
```

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
```
bash ./03_initdb.sh
```
Initialize a deepgreen database instance.  Hit [y].
After this step, you have a running database.   
Verify that you can connect to the database.
```
source deepgreendb/greenplum_path.sh
psql
```

## 04\_xdrive.sh
Setup xdrive and related stuff.
```
bash ./04_xdrive.sh
```

## 05\_sql.sh
Setup a bunch of SQL scrtips.  You will see a few ERROR: xxx does not exist.  
These are OK (try to drop a bunch of old table/functions before create new one).
```
bash ./05_sql.sh
```
At this time, you should be able to see image files from database.  Verify by running
the following command
```
source deepgreendb/greenplum_path.sh
psql
```
And in your sql prompt, run
```
select dir, basename, size from imagefiles limit 10;
```
Note that you probably do not want do do
```
select * from imagefiles
```
`*` will pull in all the content of imagefiles.   While the database will run fine, your 
console/terminal probably won't be able to handle it.

## Start googlenet server.
cd to py dir, edit conda2.sh, pointing MLSUITE_ROOT and CONDA2 to the 
ml-suite and anaconda2 installation.

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


