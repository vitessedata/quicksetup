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

## 

