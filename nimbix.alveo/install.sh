
#!/bin/bash 

set -e 
set -x

# env.sh, setup environment.
function fatal 
{
	echo 
	echo ERROR: "$@"
	echo 
	exit 1
}

function pass
{
	echo '[OK]'
}

function fail
{
	echo '[FAIL]'
	if [ $1 ]; then echo "$@"; fi
	exit 1
}

# Scripts dir.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"

# All data resides in the following dir.
export DATADIR=$DIR/data
export MASTER_DATA_DIRECTORY=$DATADIR/dg-1

export GOPATH=$HOME/go
export PATH=$PATH:/usr/local/go/bin

# 00_setup.sh
# install necessary python stuff.
sudo apt update
sudo apt install -y tmux
sudo apt install -y python-opencv
sudo apt install -y python-protobuf 
sudo apt install -y python-pip
sudo pip install --upgrade pip
sudo pip install --upgrade protobuf
sudo pip install face_recognition

# /bin/sh was symlinked to /bin/dash in ubuntu, not good.
sudo rm /bin/sh
sudo ln -s /bin/bash /bin/sh

# 01_download.sh 
echo "Checking data dir $DATADIR ..."
(mkdir -p $DATADIR && cd $DATADIR && touch ./.touch) && pass || fail

wget https://s3.amazonaws.com/vitessedata/download/deepgreendb.18.19.ubuntu16.x86_64.190710.bin && pass || fail
wget https://dl.google.com/go/go1.9.5.linux-amd64.tar.gz && pass || fail
wget http://www.vision.caltech.edu/Image_Datasets/Caltech101/101_ObjectCategories.tar.gz
wget https://github.com/vitessedata/quicksetup/archive/master.zip 
