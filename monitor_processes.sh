#!/bin/bash
# Usage: ./monitor_processes.sh <pid_of_root_mininet> <log_file>
# "root_mininet" is the process that spawns the mininet network (created with the command sudo mn ...)
# Find its PID with ps -aux | grep 'sudo mn'
# This script monitors all its descendants using top in batch mode to log_file.
if [ $# -lt 1 ] || [ $# -gt 2 ]
then
	echo "Usage: ./monitor_processes.sh <pid_of_root_mininet> <log_file> OR ./monitor_processes.sh <log_file>"
else
	if [ $# -eq 2 ]
	then
		proc_list=$(pstree -p $1 | grep -o '([0-9]\+)' | head -20 | grep -o '[0-9]\+' | tr '\n' ',' | rev | cut -c2- | rev)
		top -n 100 -b -p$proc_list > $2
	else
		top -n 100 -b > $1
	fi
fi
