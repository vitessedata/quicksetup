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

# Somehow, docker may not set $USER
export USER=$(whoami)

# All data resides in the following dir.
export DATADIR=$DIR/data
export MASTER_DATA_DIRECTORY=$DATADIR/dg-1

export GOPATH=$HOME/go
export PATH=$PATH:/usr/local/go/bin


