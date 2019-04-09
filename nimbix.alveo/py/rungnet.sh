#!/bin/bash

rm -f /tmp/ml.sock
python ./googlenet.py server /tmp/ml.sock
