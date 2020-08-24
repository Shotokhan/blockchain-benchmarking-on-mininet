#!/bin/bash
cd $HOME
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
if [ ! -d "$HOME/blockchain-benchmarking-on-mininet" ]; then
	git clone https://github.com/Shotokhan/blockchain-benchmarking-on-mininet
fi
cp -r blockchain-benchmarking-on-mininet/* ./
cp custom/* mininet/custom
if [ -f "decrypt.sh" && -f "get_java.sh" ]; then
	./get_java.sh
	./decrypt.sh
fi
sudo mkdir /usr/java
sudo mv jre1.8.0_201 /usr/java/
echo 'export PATH="/usr/java/jre1.8.0_201/bin/:$PATH"' >> ./.bashrc
source ./.bashrc
sudo apt-get -y install curl
mkdir Captures
mkdir Proc_Logs
mkdir Nodes_Logs
sudo date -s "$(wget -qSO- --max-redirect=0 google.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z"
sudo apt-get -y install python-matplotlib
# wget https://bitbucket.org/Jelurida/nxt-evaluation/downloads/nxt-eval-client-1.11.5.sh
# sudo ./nxt-eval-client-1.11.5.sh
# rm -f nxt-eval-client-1.11.5.sh
sudo apt-get -y install software-properties-common
sudo add-apt-repository -y ppa:ethereum/ethereum
sudo apt-get -y update
sudo apt-get -y install ethereum
# mkdir ethnet
# cd ethnet
# echo "password" > pwdfile
# bootnode -genkey boot.key
# bootnode -nodekey boot.key -writeaddress > public_boot
