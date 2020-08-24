#!/bin/bash
if [ $# -ne 1 ]
then
	echo "Usage: ./clone_folder.sh <number_of_hosts>"
else
	n_hosts=$1
	for((i=1;i<=$n_hosts;i++))
	do
		cp -r /home/mininet/NXT-EVAL "/home/mininet/EVAL-NXT-h$i"
	done
fi
