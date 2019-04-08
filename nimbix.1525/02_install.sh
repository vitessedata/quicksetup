#!/bin/bash

source env.sh

mkdir -p ~/go
sudo tar -C /usr/local -xzf go1.9.5.linux-amd64.tar.gz

bash ./deepgreendb.*.bin
