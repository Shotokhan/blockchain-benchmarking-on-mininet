#!/bin/bash
rm -f Proc_Logs/*
rm -f Captures/*
rm -f Analysis/*.png
rm -f Analysis/*.csv
rm -f Nodes_Logs/*
rm -f Test_Logs/*
sudo rm -r EVAL-NXT-h*
sudo rm -r ethnet/node*
sudo mn -c

