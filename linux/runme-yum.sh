#!/bin/bash
# FOR SYSTEMS WITH YUM ONLY
sudo yum -y install smartmontools
cd ../lib/pySMART-master
sudo python setup.py install

sudo yum -y --enablerepo=extras install epel-release
sudo yum -y update
sudo yum -y install python-pip

sudo python -m pip --proxy=http://cias-http-proxy.rit.edu:3128 install --upgrade pip

sudo pip --proxy=http://cias-http-proxy.rit.edu:3128 install postgres
sudo pip --proxy=http://cias-http-proxy.rit.edu:3128 install mysql-connector==2.1.4
sudo pip --proxy=http://cias-http-proxy.rit.edu:3128 install update mysql-connector

sudo mkdir /usr/local/bin/dbtshddtool/
sudo mkdir /usr/local/bin/dbtshddtool/lib/

cd ../../src/
sudo cp dbts-auto.py  /usr/local/bin/dbtshddtool/
cd ../linux/
sudo cp runhddtool.sh /usr/local/bin/dbtshddtool/
cd ../lib/
sudo cp dbts.config /usr/local/bin/dbtshddtool/lib/

sudo chmod +x /usr/local/bin/dbtshddtool/runhddtool.sh

sudo crontab -l | (cat; echo "0 * * * * /usr/local/bin/dbtshddtool/runhddtool.sh >/dev/null 2>&1";)  | sudo crontab -
