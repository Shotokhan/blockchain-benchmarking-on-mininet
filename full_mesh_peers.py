import os
import sys


def host_numToIp(host_num):
    y = host_num // 256
    z = host_num % 256
    ip = "10.0.{}.{}".format(str(y),str(z))
    return ip


if __name__=="__main__":
    if len(sys.argv) != 2:
        print("Usage: python full_mesh_peers.py <number_of_hosts>")
    else:
        os.system("/home/mininet/clone_folder.sh {}".format(sys.argv[1]))
        properties = []
        firstProp = "nxt.myAddress="
        secondProp = "nxt.testnetPeers="
        with open('/home/mininet/nxt.properties_toModify', 'r') as f:
            line = f.readline()
            while line:
                if '#' not in line and 'nxt' in line:
                    properties.append(line)
                line = f.readline()
        # first 2 properties are different for each host
        properties = properties[2:]
        host_nums = set([i for i in range(1, int(sys.argv[1])+1)])
        for i in host_nums:
            with open("/home/mininet/EVAL-NXT-h{}/conf/nxt.properties".format(str(i)), 'w') as f:
                f.write("{}{}".format(firstProp, host_numToIp(i)) + os.linesep)
                peers = host_nums.difference(set([i]))
                ip_peers = [host_numToIp(i) for i in peers]
                f.write("{}{}".format(secondProp, ";".join(ip_peers)) + os.linesep)
                for prop in properties:
                    f.write(prop + os.linesep)
