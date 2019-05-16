#!/bin/bash

rm -f /tmp/ml.sock
(nohup python ./googlenet.py > /tmp/gnet.out 2>&1) &
sleep 1
chmod 777 /tmp/ml.sock
