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

## bash ./00\_setup.sh
Install python protobuf binding and tmux.   There is a reasonable
simple tmux.conf file in ../docker/misc, you can copy it 
to ~/.tmux.conf   The tmux.conf just set some simple color scheme
and set tmux key to `^A` instead of `^B`.

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
a tmux session, let it stay there printing debug info.
```
sudo bash
cd py
source /root/vitessedata/huaweicloud-fpga/fp1/setup.sh
conda activate ml-suite
./rungnet.sh 
```

This is yet another ml-suite flavor.  I lost count how many flavors.
Huawei cloud installation (at least the process we carried out) rely
heavily on being root.  Somehow, we should fix this ...   Later.

## Test 
As deepgreen user, cd to /quicksetup/py
```
sudo chmod 777 /tmp/ml.sock
python gnetcli.py $PWD
```
If everything goes well, you should see a bunch of test images classified by googlenet.

## SQL
Note that you must start googlenet.py and do the chmod as above.
```
psql -f ../sql/gnet2.sql
```
Should classify bunch of pandas.


