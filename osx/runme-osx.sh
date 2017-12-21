#!/bin/bash

/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

brew install smartmontools

cd ../lib/pySMART-master
sudo python setup.py install

sudo easy_install pip

sudo python -m pip install --upgrade pip
sudo pip install postgres
sudo pip install mysql-connector==2.1.4
sudo pip install update mysql-connector

sudo mkdir /Applications/Utilities/dbtshddtool/
sudo mkdir /Applications/Utilities/dbtshddtool/lib/

cd ../../src/
sudo cp dbts-auto.py /Applications/Utilities/dbtshddtool/
cd ../linux/
sudo cp runhddtool.sh /Applications/Utilities/dbtshddtool/
cd ../lib/
sudo cp dbts.config /Applications/Utilities/dbtshddtool/lib/

sudo chmod +x /Applications/Utilities/dbtshddtool/runhddtool.sh