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




