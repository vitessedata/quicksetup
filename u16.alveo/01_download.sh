#!/bin/bash

source env.sh

echo "Checking data dir $DATADIR ..."
(mkdir -p $DATADIR && cd $DATADIR && touch ./.touch) && pass || fail

wget https://s3.amazonaws.com/vitessedata/download/deepgreendb.18.16.ubuntu16.x86_64.190419.bin > /dev/null 2>&1 && pass || fail
wget https://dl.google.com/go/go1.9.5.linux-amd64.tar.gz > /dev/null 2>&1 && pass || fail
wget http://www.vision.caltech.edu/Image_Datasets/Caltech101/101_ObjectCategories.tar.gz > /dev/null 2>&1 && pass || fail

# install necessary python stuff.
# pip install --upgrade protobuf --user
# pip install face_recognition --user

