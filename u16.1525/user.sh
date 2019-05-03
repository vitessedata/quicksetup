#!/bin/bash

/usr/sbin/groupadd deepgreen \
    && /usr/sbin/useradd deepgreen -g deepgreen -m \
    && echo deepgreen:deepGr33n | chpasswd \
    && echo "deepgreen ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

