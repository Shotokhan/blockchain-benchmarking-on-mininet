"""
Marco Carlo Feliciano
This example contains tcpdump and monitoring of CPU/memory usage, creation of folders for NXT peers, analysis of processes logs.
I also added configuration of network parameters.
"""

from mininet.net import Mininet
from mininet.log import setLogLevel
import time
import os
import sys
from topos_for_blockchain import StarTopo
from util_for_blockchain import *

sys.path.append("/home/mininet/Analysis")
from proc_logs_analysis import log_analysis
from make_plots import make_plots
from tshark_CSV import tshark_output_to_CSV


def run(number_of_hosts):
    setLogLevel('info')
    os.system('sudo rm -r /home/mininet/EVAL-NXT-h*')
    os.system('python /home/mininet/full_mesh_peers.py {}'.format(number_of_hosts))
    passphrases = {"h{}".format(i):(i-1)%10 for i in range(1, number_of_hosts+1)}
    unique = time.strftime("%d_%m_%Y_%H:%M", time.localtime())
    script_name = "{}_star_topology_NXT".format(str(number_of_hosts))
    print("{}: started at {}".format(script_name, unique))
    hosts = ["h{}".format(i) for i in range(1, number_of_hosts+1)]
    topo = StarTopo(number_of_hosts)
    net = Mininet(topo, autoSetMacs=True)
    net.start()
    configNetParams(net, hosts)
    # I run only one sniffer otherwise it doesn't work well with many tcpdumps open; and also because the traffic is the same on all interfaces.
    net.nameToNode['h1'].cmd("tcpdump -s0 -i h1-eth0 -U -w /home/mininet/Captures/traffic_h1_{}_{}.pcap &".format(script_name, unique))
    # the sleeps are to make tcpdump log well before traffic generation and before stop (stopping the net kills the processes that are writing to log file)
    time.sleep(2)
    for host in hosts:
        net.nameToNode[host].cmd("cd /home/mininet/EVAL-NXT-{}".format(host))
        net.nameToNode[host].cmd("nohup timeout 300 ./run.sh > /home/mininet/Nodes_Logs/log_{}_{}_{} &".format(host, script_name, unique))
    # wait for initialization
    print('Waiting for initialization of NXT nodes')
    time.sleep(20)
    print('Inizialization done')
    net.nameToNode['h1'].cmd("/home/mininet/monitor_processes.sh /home/mininet/Proc_Logs/processes_log_{}_{} &".format(script_name, unique))
    # other commands here
    for host in hosts:
        net.nameToNode[host].cmd("curl --data 'secretPhrase={}' http://{}:6876/nxt?requestType=startForging".format(passphrases[host], hostToIp(host)))
    # leave the nodes some time forging
    time.sleep(180)
    for host in hosts:
        try:
            net.nameToNode[host].cmd("curl --data 'secretPhrase={}' http://{}:6876/nxt?requestType=stopForging".format(passphrases[host], hostToIp(host)))
        except:
            pass
    ############
    time.sleep(5)
    resetNetParams(net, hosts)
    net.stop()
    proc_log_path = '/home/mininet/Proc_Logs/'
    proc_log_name = 'processes_log_{}_{}'.format(script_name, unique)
    log_analysis("{}{}".format(proc_log_path, proc_log_name), ["java"])
    make_plots('/home/mininet/Analysis/analysis_{}.csv'.format(proc_log_name))
    tshark_output_to_CSV('/home/mininet/Analysis/traffic_volume_{}_{}.csv'.format(script_name, unique), '/home/mininet/Captures/traffic_h1_{}_{}.pcap'.format(script_name, unique), 'websocket')
    return "{}_{}".format(script_name, unique)
        

topos = { 'mytopo': ( lambda: StarTopo() ) } 

if __name__=="__main__":
    setLogLevel('info')
    if len(sys.argv) != 2:
        print("Usage sudo python n_star_topology_NXT.py <number_of_hosts>")
    else:
        name_for_output = run(int(sys.argv[1]))
        print(name_for_output)
        
        
        
