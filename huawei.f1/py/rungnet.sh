#!/bin/bash

export MLSUITE_ROOT=/root/vitessedata/ml-suite
source $MLSUITE_ROOT/overlaybins/setup.sh huawei

rm -f /tmp/ml.sock
python ./googlenet.py 
