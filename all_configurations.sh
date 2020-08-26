#!/bin/bash
sudo ip link set eth1 up
sudo dhclient eth1 -v 
sudo groupadd pcap
sudo usermod -a -G pcap $USER
sudo chgrp pcap /usr/sbin/tcpdump
sudo chmod 750 /usr/sbin/tcpdump
sudo setcap cap_net_raw,cap_net_admin=eip /usr/sbin/tcpdump
sudo apt-get -y update
sudo apt-get -y install gnupg-agent
sudo apt-get -y install gnupg2
if [ ! -d "blockchain-benchmarking-on-mininet" ]; then
	git clone https://github.com/Shotokhan/blockchain-benchmarking-on-mininet
fi
if [ -f "decrypt.sh" ] && [ -f "get_java.sh" ]; then
	./get_java.sh
	./decrypt.sh
fi
sudo mkdir /usr/java
sudo mv jre1.8.0_201 /usr/java/
echo 'export PATH="/usr/java/jre1.8.0_201/bin/:$PATH"' >> $HOME/.bashrc
source $HOME/.bashrc
sudo apt-get -y install curl
sudo timedatectl set-timezone UTC
sudo date -s "$(wget -qSO- --max-redirect=0 google.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z"
sudo apt-get -y install python-matplotlib
sudo apt-get -y install software-properties-common
sudo add-apt-repository -y ppa:ethereum/ethereum
sudo apt-get -y update
sudo apt-get -y install ethereum
