# blockchain-benchmarking-on-mininet
Benchmarking of blockchain technologies in emulated network environment

To download the VM: https://github.com/mininet/mininet/releases/download/2.2.2/mininet-2.2.2-170321-ubuntu-14.04.4-server-i386.zip
In VirtualBox or similar, configure an host only network adapter as described in http://mininet.org/vm-setup-notes/

You can easily setup the test environment by running all_configurations.sh script; but, the script will ask you a password to decrypt the file which contains Oracle Java 8. It is of personal use, so I can't openly share it: this is the private part of this repository. But anyone can download it here: https://www.oracle.com/java/technologies/javase/javase8-archive-downloads.html#license-lightbox after registering to Oracle. Then, to execute all_configurations.sh , extract the java archive in your home folder, and create a decrypt.sh script that does nothing more than a hello world. Same for get_java.sh

To properly run the experiments and log the results, change directory in /home/mininet/mininet/custom on the VM, and then:

sudo nohup python -u run_experiments_NXT.py <test_case_ID> > /home/mininet/"test_log_NXT_<test_case_ID>_$(date -Is)" & 
sudo nohup python -u run_experiments_ETH.py <test_case_ID> > /home/mininet/"test_log_ETH_<test_case_ID>_$(date -Is)" &

Where test_case_ID can be 0, 1, 2 or 3:
0 for all tests
1 for the test with an incremental number of nodes [5, 10... 40] in a star topology, to evaluate only usage of CPU and RAM used by blockchain nodes (traffic is measured too but it is not an usual traffic because nodes only forge, without processing transactions). Nodes forge for 180 seconds.
2 for the test with an incremental number of transactions [250, 500, 1000, 2500, 4000, 5000, 10000] in a tree topology with an incremental depth [1, 2, 3], to evaluate TPS rate with respect to number of TX and number of peers. The tree topology has a load generator client at its root, and to each switch that is directly connected to hosts, it is connected another switch, that has an host connected for each host of the other switch: these hosts are the observing clients. Nodes process transactions for 200 seconds.
3 for a test like test 2, but with a link that goes down after 50 seconds, and goes up again at second 100 from start of the test: therefore, the link is up for the first 50 seconds, then down for 50 seconds and again up for 100 seconds. The link that goes down is always the one between the root switch and its right child, partitioning the network in half.

I suggest to not use test_case_ID = 0 for two reasons: the first is about the test log in output, it would be the same file for different tests; the second is about the fact that running too many tests in the same process is sometimes "buggy", whereas it is guaranteed that running 1, 2 or 3 has no bugs.
Output files are in the folders Analysis, Captures, Nodes_Logs and Proc_Logs. Proc_Logs are not very useful, the output of their analysis is already in the Analysis folder; meanwhile, despite traffic is analyzed, Captures can still be interesting to view in Wireshark. Nodes_Logs contain the logs of blockchain's nodes, they are not analyzed but they can be interesting to view.
