import os
import sys
import json


sys.path.append("/home/mininet/mininet/custom")
from util_for_blockchain import hostToIp

def run(num_nodes):
    os.system("rm -r /home/mininet/ethnet/node*")
    os.system("/home/mininet/create_eth_nodes.sh {}".format(num_nodes))
    nodes = {}
    for i in range(1, num_nodes+1):
        path = "/home/mininet/ethnet/node{}/keystore".format(i)
        filename = os.listdir(path)[0]
        with open("{}/{}".format(path, filename), 'r') as f:
            data = f.readline()
        parsed_data = json.loads(data)            
        nodes["node{}".format(i)] = "0x{}".format(parsed_data['address'])
    f = open("/home/mininet/ethnet/ethnet.json", 'r')
    # json.load is different from json.loads
    gen = json.load(f)
    f.close()
    extraData = "0x{}{}{}{}".format(64*"0", nodes["node1"][2:], nodes["node2"][2:], 130*"0")
    balance = "0x2{}".format(62*"0")
    gen["extraData"] = extraData
    for key in nodes.keys():
        gen["alloc"][nodes[key][2:]] = {'balance': balance}
    with open("/home/mininet/ethnet/genesis.json", 'w') as f:
        json.dump(gen, f)
    for key in nodes.keys():
        os.system("geth --datadir /home/mininet/ethnet/{}/ init /home/mininet/ethnet/genesis.json".format(key))
    for i in range(1, num_nodes+1):
        filename = "/home/mininet/ethnet/node{}/geth/static-nodes.json".format(i)
        os.system("touch {}".format(filename))
        os.system("""echo "[" >> {}""".format(filename))
        for j in range(1, num_nodes+1):
            if j == num_nodes or (j == (num_nodes - 1) and i == num_nodes):
                last_char = ""
            else:
                last_char = ","
            if j != i:
                os.system("""echo ' "'"enode://$(bootnode -nodekey /home/mininet/ethnet/node{}/geth/nodekey -writeaddress)@{}:30310"'"{}' >> {}""".format(j, hostToIp("h{}".format(j)), last_char, filename))
        os.system("""echo "]" >> {}""".format(filename))        
    return nodes
    


if __name__=="__main__":
    if len(sys.argv) != 2:
        print("Usage: python eth_config.py <number_of_nodes>")
    else:
        num_nodes = int(sys.argv[1])
        if num_nodes < 2:
            print("At least 2 nodes required")
        else:
            nodes = run(num_nodes)
            print(nodes)
        
