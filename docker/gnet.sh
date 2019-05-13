#!/bin/bash 
export MLSUITE_ROOT=/opt/ml-suite
source $MLSUITE_ROOT/overlaybins/setup.sh alveo-u200

rm -f /tmp/ml.sock
python /home/mluser/quicksetup/py/googlenet.py
