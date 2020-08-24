#!/bin/bash
# if you use virtualBox and you have set-up an host-only network to connect guest with host with SSH, you need to assign eth1 an IP address to connect the VM to the Internet
sudo ip link set eth1 up
sudo dhclient eth1 -v 
