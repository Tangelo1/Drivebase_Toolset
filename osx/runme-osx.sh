#!/bin/bash

xcode-select --install

/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

brew install smartmontools
ln -s /usr/local/sbin/smartctl /usr/local/bin

cd ../pySMART-master
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
cd ../osx/
sudo cp runhddtool.sh /Applications/Utilities/dbtshddtool/
cd ../lib/
sudo cp dbts.config /Applications/Utilities/dbtshddtool/lib/

sudo chmod +x /Applications/Utilities/dbtshddtool/runhddtool.sh

cd ../osx/
sudo cp edu.rit.cias.txacias.dbtshddtool.plist /Library/LaunchDaemons
sudo launchctl load -w /Library/LaunchDaemons/edu.rit.cias.txacias.dbtshddtool.plist