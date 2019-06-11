Deepgreen ml-suite docker image
===============================

To use static ip, first create a network
```
docker network create --subnet=172.20.0.0/16 dgnet

```

Run ml-suite docker  
====================
You can download and run the docker image from dockerhub.

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


Build Docker Image
===================
Our docker image on dockerhub is built with the docker\_build.sh.  
You do *not* need to do the following is you just want to run or test our
docker image from dockerhub.   

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


Running locally built docker image 
----------------------------------
```
bash docker_run.sh
```
This will run the locally built docker.   

