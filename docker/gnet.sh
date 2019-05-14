#!/bin/bash

export MLSUITE_ROOT=/opt/ml-suite
source $MLSUITE_ROOT/overlaybins/setup.sh alveo-u200

export MLSUITE_MODE=deployment_modes

rm -f /tmp/ml.sock
# python ../py/googlenet.py > /tmp/gnet.out 2>&1
python /home/mluser/quicksetup/py/googlenet.py 
