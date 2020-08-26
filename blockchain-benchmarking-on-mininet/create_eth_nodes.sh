#!/bin/bash
if [ $# -ne 1 ]
then
	echo "Usage: ./create_eth_nodes.sh <number_of_nodes>"
else
	n_hosts=$1
	for((i=1;i<=$n_hosts;i++))
	do
		mkdir "ethnet/node$i"
		geth --datadir "ethnet/node$i/" account new --password "ethnet/pwdfile"
	done
fi 
