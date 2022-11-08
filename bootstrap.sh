#!/bin/bash

apt-get -y update

apt-get -y install python3 python3-venv python3-pip python3-setuptools 

pip3 install flask jinja2 

apt-get -y install iptables-services iptables-dev

