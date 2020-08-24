#!/bin/bash
rm -f /home/mininet/Proc_Logs/*
rm -f /home/mininet/Captures/*
rm -f /home/mininet/Analysis/*.png
rm -f /home/mininet/Analysis/*.csv
rm -f /home/mininet/Nodes_Logs/log_*
rm -f /home/mininet/test_log_*
sudo rm -r /home/mininet/EVAL-NXT-h*
sudo rm -r /home/mininet/ethnet/node*
sudo mn -c

