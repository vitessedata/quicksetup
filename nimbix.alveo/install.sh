
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
sudo apt install -y python3-pip
sudo pip install --upgrade pip
sudo pip install --upgrade protobuf
sudo pip install face_recognition
sudo pip3 install --upgrade pip
sudo pip3 install numpy \
	opencv-python \
	jupyter \
	ipykernel \
	matplotlib \
	enum34 



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

# 02_install.sh
mkdir -p ~/go
sudo tar -C /usr/local -xzf go1.9.5.linux-amd64.tar.gz
printf "\n\n\n" | bash ./deepgreendb.*.bin --accept-license
unzip master.zip

# 03_initdb.sh
source ./deepgreendb/greenplum_path.sh

rm -fr data && pass || fail
mkdir -p data && pass || fail
rm -fr monagent && pass || fail
mkdir -p monagent && pass || fail

cp quicksetup-master/nimbix.alveo/cluster.conf .
cp quicksetup-master/nimbix.alveo/hostfile .

# I don't know why, but gpinitsystem will exit current shell.
# the || pass is a hack to work around this.
gpinitsystem -a -q -c cluster.conf --lc-collate=C || pass
createdb nimbix 

# 04_xdrive.sh
rm -fr xdrive && pass || fail
mkdir -p xdrive && pass || fail
mkdir -p xdrive/images && pass || fail

rm -f ./xdrive.toml 

echo "
[xdrive]
dir = \"$DIR/xdrive\"
pluginpath = [\"$DIR/xdrive/plugin\"] 
port=31416
host = [ \"localhost\" ]

[[xdrive.mount]]
name = \"images\" 
argv = [\"dgtools/ls_file\", \"$DIR/xdrive/images\"] 
" >> xdrive.toml

xdrctl deploy ./xdrive.toml
xdrctl start ./xdrive.toml

mkdir -p $DIR/xdrive/plugin/dgtools && pass || fail
cp quicksetup-master/xdrive/ls_file $DIR/xdrive/plugin/dgtools/ && pass || fail
tar -C ./xdrive/images -xzf 101_ObjectCategories.tar.gz && pass || fail
mkdir -p ./xdrive/images/search
cp ./xdrive/images/101_ObjectCategories/soccer_ball/image_0001.jpg ./xdrive/images/search/object.jpg

# install sql scripts
dg setup -all nimbix
psql -f quicksetup-master/sql/img.sql nimbix

# install python dg module (for jupyter).
(cd quicksetup-master/py/lib; python3 setup.py install --user)
