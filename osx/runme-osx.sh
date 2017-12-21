#!/bin/bash

/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

brew install smartmontools

cd ../lib/pySMART-master
sudo python setup.py install

sudo python -m pip install --upgrade pip
sudo pip install postgres
sudo pip install mysql-connector==2.1.4
sudo pip install update mysql-connector

sudo mkdir /Applications/Utilites/dbtshddtool/
sudo mkdir /Applications/Utilites/dbtshddtool/lib/

cd ../../src/
sudo cp dbts-auto.py /Applications/Utilites/dbtshddtool/
cd ../linux/
sudo cp runhddtool.sh /Applications/Utilites/dbtshddtool/
cd ../lib/
sudo cp dbts.config /Applications/Utilites/dbtshddtool/lib/

sudo chmod +x /Applications/Utilites/dbtshddtool/runhddtool.sh