from mininet.net import Mininet
from mininet.log import setLogLevel
import time
import sys
from Util.topos_for_blockchain import StarTopo
from Util.util_for_blockchain import *
from Analysis.proc_logs_analysis import log_analysis
from Analysis.make_plots import make_plots
from Analysis.tshark_CSV import tshark_output_to_CSV
from eth_config import run as ethereum_config


def run(number_of_hosts):
    setLogLevel('info')
    eth_nodes = ethereum_config(number_of_hosts)
    host_to_ethAddr = lambda host: eth_nodes["node{}".format(host[1:])]
    unique = time.strftime("%d_%m_%Y_%H:%M", time.localtime())
    script_name = "{}_star_topology_ETH".format(str(number_of_hosts))
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
        net.nameToNode[host].cmd("cd ethnet")
    for host in hosts:
        net.nameToNode[host].cmd("nohup timeout 300 geth --ipcdisable --datadir node{}/ --syncmode 'full' --port 30310 --nat extip:{} --http --http.addr '{}' --http.port 8501 --http.api 'personal,debug,eth,net,web3,txpool,miner' --networkid 700 -unlock '{}' --password pwdfile --mine --miner.gasprice '1' --miner.gaslimit '94000000' --miner.gastarget '1' --allow-insecure-unlock --nodiscover > ../Nodes_Logs/log_{}_{}_{} &".format(host[1:], hostToIp(host), hostToIp(host), host_to_ethAddr(host), host, script_name, unique))
    # wait for initialization
    print('Waiting for initialization of ETH nodes')
    time.sleep(20)
    print('Inizialization done')
    net.nameToNode['h1'].cmd("../Util/monitor_processes.sh ../Proc_Logs/processes_log_{}_{} &".format(script_name, unique))
    # other commands here
    time.sleep(180)
    ############
    time.sleep(5)
    resetNetParams(net, hosts)
    net.stop()
    proc_log_name = 'processes_log_{}_{}'.format(script_name, unique)
    log_analysis("Proc_Logs/{}".format(proc_log_name), ["geth"])
    make_plots('Analysis/analysis_{}.csv'.format(proc_log_name))
    tshark_output_to_CSV('Analysis/traffic_volume_{}_{}.csv'.format(script_name, unique), 'Captures/traffic_h1_{}_{}.pcap'.format(script_name, unique))
    return "{}_{}".format(script_name, unique)
        

topos = { 'mytopo': ( lambda: StarTopo() ) } 

if __name__=="__main__":
    setLogLevel('info')
    if len(sys.argv) != 2:
        print("Usage sudo python n_star_topology_ETH.py <number_of_hosts>")
    else:
        name_for_output = run(int(sys.argv[1]))
        print(name_for_output)
        
        
        

