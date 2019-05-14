#!/bin/bash

# locale en_US.UTF-8 has an alias.
sudo locale-gen en_US.utf8 
# Start ssh
sudo service ssh start
#

MYIP="$(hostname -I)"

# Some fixes for mluser setting
echo ". /opt/ml-suite/overlaybins/setup.sh $PLATFORM" >> ~/.bashrc
echo ". /home/mluser/quicksetup/u16.alveo/deepgreendb/greenplum_path.sh" >> ~/.bashrc
ssh-keyscan localhost >> /home/mluser/.ssh/known_hosts
ssh-keyscan 0.0.0.0 >> /home/mluser/.ssh/known_hosts
ssh-keyscan dg >> /home/mluser/.ssh/known_hosts
ssh-keyscan $MYID >> /home/mluser/.ssh/known_hosts

# Create database.
(cd /home/mluser/quicksetup/u16.alveo && bash 03_initdb.sh)
(cd /home/mluser/quicksetup/u16.alveo && bash 04_xdrive.sh)
(cd /home/mluser/quicksetup/u16.alveo && bash 05_sql.sh)

# Start gnet
# This is rather tricky: docker does not like systemd, so that any attempt to 
# use systemd will incur horrible hack.   Note that we setup a bunch of env
# in side the gnet.sh, so better let the whole gnet.sh run nohup.
(nohup bash /home/mluser/quicksetup/docker/gnet.sh > /tmp/gnet.out 2>&1) &

# jupyter
jupyter notebook --generate-config
echo "c.NotebookApp.ip = '*'" >> /home/mluser/.jupyter/jupyter_notebook_config.py
echo "c.NotebookApp.open_browser = False" >> /home/mluser/.jupyter/jupyter_notebook_config.py

# tmux
cp /home/mluser/quicksetup/docker/misc/tmux.conf ~/.tmux.conf

# Start a shell
/bin/bash 

