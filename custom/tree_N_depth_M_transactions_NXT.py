"""
Marco Carlo Feliciano
This example contains tcpdump and monitoring of CPU/memory usage, creation of folders for NXT peers, analysis of processes logs.
I also added configuration of network parameters, analysis of traffic volume between peers, and TPS.
"""

from mininet.net import Mininet
from mininet.log import setLogLevel
import time
import os
import sys
from NXT_observingClient import observingClient
from topos_for_blockchain import Tree_SUT as TreeTopo
from util_for_blockchain import *

sys.path.append("/home/mininet/Analysis")
from proc_logs_analysis import log_analysis
from make_plots import make_plots
from observers_TPS_csv import export_TPS_to_CSV
from tshark_CSV import tshark_output_to_CSV
from tshark_CSV import tshark_total_traffic
    

def run(depth, number_of_TX):
    setLogLevel('info')
    os.system('sudo rm -r /home/mininet/EVAL-NXT-h*')
    os.system('python /home/mininet/full_mesh_peers.py {}'.format(2**depth))
    # you can change passphrases
    number_of_hosts = 2**depth
    passphrases = {"h{}".format(i):(i-1)%10 for i in range(1, number_of_hosts+1)}
    unique = time.strftime("%d_%m_%Y_%H:%M", time.localtime())
    script_name = "tree_{}_depth_{}_transactions_NXT".format(str(depth), str(number_of_TX))
    print("{}: started at {}".format(script_name, unique))
    hosts = ["h{}".format(i) for i in range(1, number_of_hosts+1)]
    topo = TreeTopo(depth)
    net = Mininet(topo, autoSetMacs=True)
    net.start()
    net_hosts = ["h{}".format(i) for i in range(1, len(net.hosts)+1)]
    configNetParams(net, net_hosts)
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
    # leave the nodes some time forging and send transactions at regular intervals (a burst every 20 seconds for 10 times)
    # Start observing clients
    total_time = 200
    observers = []
    for host in hosts:
        observer = observingClient(total_time, "h{}".format(int(host[1])+number_of_hosts+1), net, host)
        observers.append(observer)
        observer.start()
    # Generate transactions
    tx_burst = 50
    n_bursts = number_of_TX // tx_burst
    # n_bursts = 10
    # tx_burst = number_of_TX // n_bursts
    amounts = [i*10**8 for i in [50, 100, 200]]
    fees = [i*10**8 for i in [1, 5, 10]]
    start = time.time()
    stop_it = False
    for i in range(n_bursts):
        print("Transaction burst number {}".format(i+1))
        # round nodes
        for j in range(tx_burst):
            host_num = j % len(hosts) + 1
            host_IP = hostToIp('h{}'.format(host_num))
            try:
                net.nameToNode['h{}'.format(number_of_hosts + 1)].cmd("curl -m 1 --data 'recipient=NXT-2543-6FUN-HS5W-BNVW6&secretPhrase={}&deadline=1440&phased=false&phasingHashedSecretAlgorithm=2&feeNQT={}&amountNQT={}' http://{}:6876/nxt?requestType=sendMoney".format(j%10, fees[j%3], amounts[j%3], host_IP))
            except:
                print("One transaction not sent to h{} due to some exception".format(host_num))
            elapsed = time.time() - start
            if elapsed >= total_time:
                stop_it = True
                break
        if stop_it:
            break
        time.sleep(total_time // n_bursts)
    for host in hosts:
        try:
            net.nameToNode[host].cmd("curl --data 'secretPhrase={}' http://{}:6876/nxt?requestType=stopForging".format(passphrases[host], hostToIp(host)))
        except:
            pass
    ############
    time.sleep(5)
    try:
        resetNetParams(net, net_hosts)
    except:
        pass
    try:
        net.stop()
    except:
        pass
    proc_log_path = '/home/mininet/Proc_Logs/'
    proc_log_name = 'processes_log_{}_{}'.format(script_name, unique)
    log_analysis("{}{}".format(proc_log_path, proc_log_name), ["java"])
    make_plots('/home/mininet/Analysis/analysis_{}.csv'.format(proc_log_name))
    obs_dict = {obs.observedHost:obs.TPS() for obs in observers}
    export_TPS_to_CSV('/home/mininet/Analysis/TPS_measures_{}_{}.csv'.format(script_name, unique), obs_dict)
    mean_TPS = sum(observer.TPS() for observer in observers) / len(observers)
    tshark_output_to_CSV('/home/mininet/Analysis/traffic_volume_{}_{}.csv'.format(script_name, unique), '/home/mininet/Captures/traffic_h1_{}_{}.pcap'.format(script_name, unique), 'websocket')
    total_traffic = tshark_total_traffic('/home/mininet/Captures/traffic_h1_{}_{}.pcap'.format(script_name, unique), ['websocket', 'http'])
    return [mean_TPS, total_traffic]
    

topos = { 'mytopo': ( lambda: TreeTopo() ) } 

if __name__=="__main__":
    if len(sys.argv) != 3:
        print("Usage sudo {} <depth> <number_of_transactions>".format(sys.argv[0]))
    else:
        depth = int(sys.argv[1])
        number_of_TX = int(sys.argv[2])
        run(depth, number_of_TX)
        
