# Vitessedata Deepgreen with ml-suite on Huawei Cloud

Huawei cloud VM will be Centos/RHEL 7.3.  After installation
user can ssh into the machine as root.

## user.sh
First, run user.sh.  This will create a sudo user called 
deepgreen.  Run 
```
su deepgreen
```
Later steps should be executed as deepgreen.  

## Get this repo
``` 
git clone https://github.com/vitessedata/quicksetup
cd quicksetup/huawei.f1
```

## bash ./01\_download.sh
Download deepgreen binary and golang 1.9.5.  It also downloads
a test image datasets.

## bash ./02\_install.sh
Will install software.

## Setup ssh keys
At this moment, it is good time to fix some ssh related stuff.
```
. env.sh
gpssh-exkeys -f hostfile
```
Also, ipv6 host will confuse deepgreen and xdrive.  edit /etc/hosts
to comment out the line of ipv6 `::1`

Follow deepgreen installation guide to config OS.  Especially, you
should pay attention to firewalld, RemoveIPC, limits.conf and sysctmctl.conf


## bash ./03\_initdb.sh
This will create a good database :-)

## bash ./04\_xdrive.sh
Set up xdrive

## bash ./05\_sql.sh
Set up a bunch of udfs.

## Start googlenet.py
Run the following as root, I would suggest running this under
a tmux session
```
sudo bash
cd py
source conda2.sh
rungnet.sh 
```
This is yet another ml-suite flavor.  I lost count how many flavors.
Huawei cloud installation (at least the process we carried out) rely
heavily on being root.  Somehow, we should fix this ...   Later.
