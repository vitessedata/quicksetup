Deepgreen ml-suite docker image
===============================

To use static ip, first create a network
```
docker network create --subnet=172.20.0.0/16 dgnet
```

Build Docker Image
===================

```
bash docker_build.sh
```

Docker image notes: 
-------------------
* user is `mluser`
* ml-suite is installed in `/opt/ml-suite`
* deepgreen is installed in `/home/mluser/quicksetup/u16.alveo/deepgreendb`
* `$MASTER_DATA_DIRECTORY` and `$PATH` should have been setup properly.
* xdrive and image files is in `/home/mluser/quicksetup/u16.alveo/images`
* a googlenet host process is started, and logging to `/tmp/gnet.out`.
* use tmux to have several shells.   tmux key binding is in ~/.tmux.conf.
  especially, we bind tmux key to `^a` (screen convention).
* cd into /home/mluser/quicksetup/docker, run runnb.sh will start a jupyter notebook.
  It will giva you a url that you can open a brower.   The really nice thing about
  jupyter is that is has a terminal :-)


Use Docker Image
=================
```
bash docker_run.sh
```
This will start a docker.  You are given a shell.   Run the following, you should 
see what googlenet classifies some panda images.

Or alternatively, you can run a docker image that we have published on dockerhub
```
bash dockerhub_run.sh
```

Test using psql
---------------

```
psql -f /home/mluser/quicksetup/sql/gnet2.sql
```

Will run a query that classifies all images under the panda dir.   The result of
the query will be image files, with classification, and score.

```
psql -f /home/mluser/quicksetup/sql/panda.sql 
```

This query will find panda from all the images (over 9000 images).   It will take
long time to run, probably one or two minutes.


Test using jupyter notebook
---------------------------

```
cd /home/mluser/quicksetup/docker
bash ./runnb.sh
```
to start a jupyter notebook.   It will print out a url, copy paste that url to a browser and 
update ip address (you can use the ip address of the host, or, 127.0.0.1 if your host is your gui workstation) 
click on nb/googlenet.ipynb.

Debug Docker 
============
```
# Change the /home/ftian/oss/quicksetup to your path
bash docker_dbg.sh
```
This will use the start.sh in the host.   You don't need
to git submit every tiny change in order to take effect. 


