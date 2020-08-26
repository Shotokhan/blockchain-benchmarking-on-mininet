import os
import sys


def host_numToIp(host_num):
    y = host_num // 256
    z = host_num % 256
    ip = "10.0.{}.{}".format(str(y),str(z))
    return ip


def run(n_hosts):
    os.system("./clone_folder.sh {}".format(n_hosts))
    properties = []
    firstProp = "nxt.myAddress="
    secondProp = "nxt.testnetPeers="
    with open('nxt.properties_toModify', 'r') as f:
        line = f.readline()
        while line:
            if '#' not in line and 'nxt' in line:
                properties.append(line)
            line = f.readline()
    # first 2 properties are different for each host
    properties = properties[2:]
    host_nums = set([i for i in range(1, int(n_hosts) + 1)])
    for i in host_nums:
        with open("EVAL-NXT-h{}/conf/nxt.properties".format(str(i)), 'w') as f:
            f.write("{}{}".format(firstProp, host_numToIp(i)) + os.linesep)
            peers = host_nums.difference({i})
            ip_peers = [host_numToIp(i) for i in peers]
            f.write("{}{}".format(secondProp, ";".join(ip_peers)) + os.linesep)
            for prop in properties:
                f.write(prop + os.linesep)


if __name__=="__main__":
    if len(sys.argv) != 2:
        print("Usage: python full_mesh_peers.py <number_of_hosts>")
    else:
        n_hosts = sys.argv[1]
        run(n_hosts)
