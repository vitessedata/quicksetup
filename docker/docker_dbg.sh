#!/bin/bash

user=`whoami`

sudo \
docker run -it --rm \
    --hostname=dg --net=dgnet --ip=172.20.0.16 -p 8888:8888 \
    --privileged -w /opt/ml-suite \
	-v /dev:/dev -v /opt/xilinx:/opt/xilinx \
	-v /home/ftian/oss/quicksetup:/quicksetup \
	--env PLATFORM=alveo-u200 \
	$user/xilinx-ml-suite:latest \
/bin/bash -c "cd /home/mluser/quicksetup && git remote update && git rebase origin/master && cd /quicksetup && bash docker/start.sh"
