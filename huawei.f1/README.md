# Vitessedata Deepgreen with ml-suite on Huawei Cloud

Huawei cloud VM will be Centos 7.4.  After installation
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

