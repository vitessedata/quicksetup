#!/bin/bash

export MLSUITE_ROOT=/opt/ml-suite
source $MLSUITE_ROOT/overlaybins/setup.sh alveo-u200

rm -f /tmp/ml.sock
nohup python ../py/googlenet.py > /tmp/gnet.out 2>&1
