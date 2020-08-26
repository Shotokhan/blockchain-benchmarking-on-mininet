def hostToIp(host):
    host_num = int(host[1:])
    y = host_num // 256
    z = host_num % 256
    ip = "10.0.{}.{}".format(str(y),str(z))
    return ip


def configLinkStatus(net, n_hosts, status):
    # status is "up" or "down"
    # this function changes the link status between the root of the tree and its right child
    # VERSION 2.2.2 of mininet doesn't have functions to delete links
    # lookup = {'up': lambda h1,h2: net.addLink(h1,h2), 'down': lambda h1,h2: net.delLink(net.linksBetween(net.nameToNode[h1], net.nameToNode[h2])[0])}
    if n_hosts == 2:
        net.configLinkStatus("s1", "h2", status)
        # lookup[status]("s1","h2")
    else:
        net.configLinkStatus("s{}".format(n_hosts - 1), "s{}".format(n_hosts - 2), status)
        # lookup[status]("s{}".format(n_hosts - 1), "s{}".format(n_hosts - 2), status)


def configNetParams(net, hosts):
    # Configuration of network parameters; I suppose delays in switches negligible compared to delays in hosts,
    # i.e. all "imperfections" of the network are aggregated in hosts
    for host in hosts:
        # 50 ms of medium delay on each interface with a std deviation of 10 ms, a normal gaussian distribution and a correlation of 25% of consecutive packets
        # 10% of probability of loss with 65% of packet loss burst, 0.01% of bit corruption, 10% of reordering and 5% of duplication
        net.nameToNode[host].cmd("sudo tc qdisc add dev {}-eth0 root netem delay 50ms 10ms 25% distribution normal loss 10% 65% corrupt 0.01% reorder 10% duplicate 5%".format(host))


def resetNetParams(net, hosts):
    for host in hosts:
        net.nameToNode[host].cmd("sudo tc qdisc del dev {}-eth0 root netem".format(host)) 
