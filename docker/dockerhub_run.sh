#!/bin/bash

sudo \
docker run -it --rm --hostname=dg --net=dgnet --ip=172.20.0.16 -p 8888:8888 --privileged -w /opt/ml-suite \
	-v /dev:/dev -v /opt/xilinx:/opt/xilinx	\
	--env PLATFORM=alveo-u200				\
	vitessedata/deepgreen-ml:latest \
/bin/bash -c "cd /home/mluser/quicksetup && git remote update && git rebase origin/master && bash docker/start.sh"
