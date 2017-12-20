#!/bin/bash

/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

brew install smartmontools

cd ../lib/pySMART-master
sudo python setup.py install

sudo python -m pip install --upgrade pip
sudo pip install postgres
sudo pip install mysql-connector==2.1.4
sudo pip install update mysql-connector
