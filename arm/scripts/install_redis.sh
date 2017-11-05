#!/bin/bash

sudo yum -y update
sudo yum -y install epel-release
sudo yum -y update
sudo yum -y install redis

# start redis
sudo systemctl start redis
# start redis on startup
sudo systemctl enable redis

# accept connection from outside of VM (make sure you are using a vnet and NSG)
echo "bind 0.0.0.0" >>  /etc/redis.conf
echo "appendonly yes" >> /etc/redis.conf
sudo systemctl restart redis
