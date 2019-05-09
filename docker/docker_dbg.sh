#!/bin/bash

sudo \
docker run -it --rm --hostname=dg --net=dgnet --ip=172.20.0.16 --privileged -w /opt/ml-suite \
	-v /dev:/dev -v /opt/xilinx:/opt/xilinx \
	-v /home/ftian/oss/quicksetup:/quicksetup \
	--env PLATFORM=alveo-u200 \
	ftian/xilinx-ml-suite:latest \
/bin/bash -c "cd /home/mluser/quicksetup && git remote update && git rebase origin/master && cd /quicksetup && bash docker/start.sh"
