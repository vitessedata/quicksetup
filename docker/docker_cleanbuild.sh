#!/usr/bin/env bash

user=`whoami`


sudo \
docker build \
  --no-cache \
  --network=host \
  -f Dockerfile \
  -t $user/xilinx-ml-suite \
  .
