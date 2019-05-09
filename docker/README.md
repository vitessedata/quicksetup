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

Use Docker Image
=================
```
bash docker_run.sh
```

Debug Docker 
============
```
# Change the /home/ftian/oss/quicksetup to your path
bash docker_dbg.sh
```
This will use the start.sh in the host.   You don't need
to git submit every tiny change in order to take effect. 


