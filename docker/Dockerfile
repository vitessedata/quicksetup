FROM ubuntu:16.04

# Libraries.
# VitesseData: Add tmux and ssh server/client
RUN apt-get update && \
 apt-get install -y --no-install-recommends apt-utils software-properties-common && \
 apt-get install -y --no-install-recommends \
 build-essential\
 ca-certificates\
 cmake\
 rsync\
 sudo\
 curl\
 wget\
 unzip\
 git\
 vim\
 graphviz\
 python-dev\
 python-skimage\
 libatlas-base-dev\
 libboost-all-dev\
 libgflags-dev\
 libgoogle-glog-dev\
 libhdf5-serial-dev\
 libleveldb-dev\
 liblmdb-dev\
 libopencv-dev\
 libprotobuf-dev\
 libsnappy-dev\
 protobuf-compiler\
 libyaml-cpp-dev\
 iproute2 \
 iputils-ping \
 less \
 locales \
 net-tools \
 openssh-client\
 openssh-server\
 ssh\
 tmux\
 && rm -rf /var/lib/apt/lists/*

# Get pip setuptools and wheel
RUN cd /tmp && curl -fSsL -O https://bootstrap.pypa.io/get-pip.py && python get-pip.py && rm get-pip.py

# Python Module Dependencies
RUN pip --no-cache-dir install\
 numpy==1.14.3\
 six==1.11.0\
 ck\
 pydot\
 pydot-ng\
 graphviz\
 h5py\
 zmq\
 protobuf\
 opencv-python\
 pytest\
 pillow\
 Flask\
 jupyter\
 ipykernel\
 matplotlib\
 enum34

# Set up non-root user for file and process ownership
RUN groupadd users -g 100 -f && useradd -g users -ms /bin/bash mluser -u 1185 && usermod -aG sudo mluser && passwd -d mluser && \
 mkdir /scratch && chmod 777 /scratch && chmod 777 /opt && chmod 777 /tmp

# VitesseData: Start sshd, password less sudo.
RUN mkdir /var/run/sshd
RUN /usr/sbin/sshd
RUN echo "mluser ALL = (ALL) NOPASSWD: ALL" >> /etc/sudoers

USER mluser


# OpenBLAS Setup To /opt/OpenBLAS
ENV LD_LIBRARY_PATH=/opt/OpenBLAS/lib
ENV OPENBLAS=/opt/OpenBLAS
RUN git clone https://github.com/xianyi/OpenBLAS.git /scratch/OpenBLAS && \
 cd /scratch/OpenBLAS && make -j NO_LAPACK=1 NO_LAPACKE=1 CC=/usr/bin/gcc USE_THREAD=1 && \
 make PREFIX=$OPENBLAS install && rm -rf /scratch/OpenBLAS && \
 cd $OPENBLAS && find . -name "*.a" -exec rm {} \; && rm -rf include 
# May need to disable AVX2 for old machines
# NO_AVX2=1

# Caffe Decent Setup To /opt/caffe
ENV CAFFE_ROOT=/opt/caffe
ENV PYCAFFE_ROOT $CAFFE_ROOT/python
ENV PYTHONPATH $PYCAFFE_ROOT:$PYTHONPATH
ENV PATH $CAFFE_ROOT/build/tools:$PYCAFFE_ROOT:$PATH
RUN mkdir /opt/caffe
ADD caffe_decent.tar.gz /opt/caffe

# Public ml-suite Setup To /opt/ml-suite switch to latest branch
ENV MLSUITE_ROOT=/opt/ml-suite
RUN git clone https://github.com/Xilinx/ml-suite.git $MLSUITE_ROOT && \
 cd $MLSUITE_ROOT && git checkout latest && git pull && rm -rf .git*

# Models Directory (Models to be pulled after container start)
RUN mkdir -p /opt/models/caffe

RUN mkdir /home/mluser/.ssh
RUN ssh-keygen -t rsa -N "" -f /home/mluser/.ssh/id_rsa
RUN cat /home/mluser/.ssh/id_rsa.pub >> /home/mluser/.ssh/authorized_keys && \
	chmod 0600 /home/mluser/.ssh/authorized_keys

# Check out vitessedata stuff.
RUN cd /home/mluser && git clone https://github.com/vitessedata/quicksetup
RUN cd /home/mluser/quicksetup/u16.alveo && sudo bash 00_root.sh
RUN cd /home/mluser/quicksetup/u16.alveo && bash 01_download.sh
RUN cd /home/mluser/quicksetup/u16.alveo && bash 02_install.sh 
# 03 - 05 will be run by docker run 
# RUN cd /home/mluser/quicksetup/u16.alveo && bash 03_initdb.sh
# RUN cd /home/mluser/quicksetup/u16.alveo && bash 04_xdrive.sh 
# RUN cd /home/mluser/quicksetup/u16.alveo && bash 05_sql.sh 

# Automatically Set Environment Variables
RUN echo "export PATH=$PATH:~/.local/bin" >> /home/mluser/.bashrc

# Expose postgres (deepgreen), ssh, http, jupyter (default)
EXPOSE 5432 22 80 8888
# Two random ports, which we use for xdrive.   Testing.
EXPOSE 27183 31416
