from mininet.net import Mininet
from mininet.log import setLogLevel
import time
import sys
from random import randint
import json
from Util.ETH_observingClient import observingClient
from Util.topos_for_blockchain import Tree_SUT as TreeTopo
from Util.util_for_blockchain import *
from Analysis.proc_logs_analysis import log_analysis
from Analysis.make_plots import make_plots
from Analysis.observers_TPS_csv import export_TPS_to_CSV
from Analysis.tshark_CSV import tshark_output_to_CSV
from Analysis.tshark_CSV import tshark_total_traffic
from eth_config import run as ethereum_config
    

def run(depth, number_of_TX):
    setLogLevel('info')
    number_of_hosts = 2**depth
    eth_nodes = ethereum_config(number_of_hosts)
    host_to_ethAddr = lambda host: eth_nodes["node{}".format(host[1:])]
    unique = time.strftime("%d_%m_%Y_%H:%M", time.localtime())
    script_name = "tree_{}_depth_{}_transactions_ETH".format(str(depth), str(number_of_TX))
    print("{}: started at {}".format(script_name, unique))
    hosts = ["h{}".format(i) for i in range(1, number_of_hosts+1)]
    topo = TreeTopo(depth)
    net = Mininet(topo, autoSetMacs=True)
    net.start()
    net_hosts = ["h{}".format(i) for i in range(1, len(net.hosts)+1)]
    configNetParams(net, net_hosts)
    # I run only one sniffer otherwise it doesn't work well with many tcpdumps open; and also because the traffic is the same on all interfaces.
    net.nameToNode['h1'].cmd("tcpdump -s0 -i h1-eth0 -U -w Captures/traffic_h1_{}_{}.pcap &".format(script_name, unique))
    # the sleeps are to make tcpdump log well before traffic generation and before stop (stopping the net kills the processes that are writing to log file)
    time.sleep(2)
    for host in net_hosts:
        net.nameToNode[host].cmd("cd ethnet")
    for host in hosts:
        net.nameToNode[host].cmd("nohup timeout 300 geth --ipcdisable --datadir node{}/ --syncmode 'full' --port 30310 --nat extip:{} --http --http.addr '{}' --http.port 8501 --http.api 'personal,debug,eth,net,web3,txpool,miner' --networkid 700 -unlock '{}' --password pwdfile --mine --miner.gasprice '1' --miner.gaslimit '94000000' --miner.gastarget '1' --allow-insecure-unlock --nodiscover > ../Nodes_Logs/log_{}_{}_{} &".format(host[1:], hostToIp(host), hostToIp(host), host_to_ethAddr(host), host, script_name, unique))
    # wait for initialization
    print('Waiting for initialization of ETH nodes')
    time.sleep(20)
    print('Inizialization done')
    net.nameToNode['h1'].cmd("../Util/monitor_processes.sh ../Proc_Logs/processes_log_{}_{} &".format(script_name, unique))
    # other commands here
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
    amounts = [50, 100, 200]
    start = time.time()
    stop_it = False
    target = "http://{}:8501"
    tx_json = lambda sender, receiver : {"from":sender, "to":receiver, "value":hex(amounts[randint(0,2)])}
    interact_json = lambda sender, receiver : json.dumps({"jsonrpc":"2.0", "method":"eth_sendTransaction", "params":[tx_json(sender, receiver)], "id":randint(10,1000)})
    interaction = """curl -m 2 -X POST -H "Content-Type: application/json" --data '{}' """
    for i in range(n_bursts):
        print("Transaction burst number {}".format(i+1))
        for j in range(tx_burst):
            host_num = j % len(hosts) + 1
            host_IP = hostToIp('h{}'.format(host_num))
            payload = interaction.format(interact_json(host_to_ethAddr("h{}".format(host_num)), "0xfb9a175032adbd79e54258cd1b4ce87f8b17e8aa")) + target.format(host_IP)
            try:
                net.nameToNode['h{}'.format(number_of_hosts + 1)].cmd(payload)
            except:
                print("One transaction not sent to h{} due to some exception".format(host_num))
            elapsed = time.time() - start
            if elapsed >= total_time:
                stop_it = True
                break
        if stop_it:
            break
        time.sleep(total_time // n_bursts)
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
    proc_log_name = 'processes_log_{}_{}'.format(script_name, unique)
    log_analysis("Proc_Logs/{}".format(proc_log_name), ["geth"])
    make_plots('Analysis/analysis_{}.csv'.format(proc_log_name))
    obs_dict = {obs.observedHost:obs.TPS() for obs in observers}
    export_TPS_to_CSV('Analysis/TPS_measures_{}_{}.csv'.format(script_name, unique), obs_dict)
    mean_TPS = sum(observer.TPS() for observer in observers) / len(observers)
    tshark_output_to_CSV('Analysis/traffic_volume_{}_{}.csv'.format(script_name, unique), 'Captures/traffic_h1_{}_{}.pcap'.format(script_name, unique))
    total_traffic = tshark_total_traffic('Captures/traffic_h1_{}_{}.pcap'.format(script_name, unique), ['udp', 'tcp'])
    return [mean_TPS, total_traffic]
    

topos = { 'mytopo': ( lambda: TreeTopo() ) } 

if __name__=="__main__":
    if len(sys.argv) != 3:
        print("Usage sudo {} <depth> <number_of_transactions>".format(sys.argv[0]))
    else:
        depth = int(sys.argv[1])
        number_of_TX = int(sys.argv[2])
        run(depth, number_of_TX)
