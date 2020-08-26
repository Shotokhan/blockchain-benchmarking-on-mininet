"""
Marco Carlo Feliciano
This example contains tcpdump and monitoring of CPU/memory usage, creation of folders for NXT peers, Analysis of processes logs.
I also added configuration of network parameters.
"""

from mininet.net import Mininet
from mininet.log import setLogLevel
import time
import os
import sys
from Util.topos_for_blockchain import StarTopo
from Util.util_for_blockchain import *
from Analysis.proc_logs_analysis import log_analysis
from Analysis.make_plots import make_plots
from Analysis.tshark_CSV import tshark_output_to_CSV
from full_mesh_peers import run as NXT_config


def run(number_of_hosts):
    setLogLevel('info')
    os.system('sudo rm -r EVAL-NXT-h*')
    NXT_config(number_of_hosts)
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
    net.nameToNode['h1'].cmd("tcpdump -s0 -i h1-eth0 -U -w Captures/traffic_h1_{}_{}.pcap &".format(script_name, unique))
    # the sleeps are to make tcpdump log well before traffic generation and before stop (stopping the net kills the processes that are writing to log file)
    time.sleep(2)
    for host in hosts:
        net.nameToNode[host].cmd("cd EVAL-NXT-{}".format(host))
        net.nameToNode[host].cmd("nohup timeout 300 ./run.sh > ../Nodes_Logs/log_{}_{}_{} &".format(host, script_name, unique))
    # wait for initialization
    print('Waiting for initialization of NXT nodes')
    time.sleep(20)
    print('Inizialization done')
    net.nameToNode['h1'].cmd("../Util/monitor_processes.sh ../Proc_Logs/processes_log_{}_{} &".format(script_name, unique))
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

    proc_log_name = 'processes_log_{}_{}'.format(script_name, unique)
    log_analysis("Proc_Logs/{}".format(proc_log_name), ["java"])
    make_plots('Analysis/analysis_{}.csv'.format(proc_log_name))
    tshark_output_to_CSV('Analysis/traffic_volume_{}_{}.csv'.format(script_name, unique), 'Captures/traffic_h1_{}_{}.pcap'.format(script_name, unique), 'websocket')
    return "{}_{}".format(script_name, unique)
        

topos = { 'mytopo': ( lambda: StarTopo() ) } 

if __name__=="__main__":
    setLogLevel('info')
    if len(sys.argv) != 2:
        print("Usage sudo python n_star_topology_NXT.py <number_of_hosts>")
    else:
        name_for_output = run(int(sys.argv[1]))
        print(name_for_output)
        
        
        
