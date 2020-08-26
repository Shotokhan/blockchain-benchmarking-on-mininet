from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel


class Tree_SUT( Topo ):
    def __init__(self, depth):
        self.depth = depth
        Topo.__init__(self)

    def build( self ):
        "Create ETH topo."

        # Add hosts and switches -- from here you can change topology
        nodes = {}
        number_of_hosts = 2**self.depth
        for i in range(1, number_of_hosts + 1):
            nodes["h{}".format(i)] = self.addHost("h{}".format(i))
        for i in range(1, number_of_hosts):
            nodes["s{}".format(i)] = self.addSwitch("s{}".format(i))
        # I need a load generator separated from the observers, to not have problems with mininet commands
        nodes["h{}".format(number_of_hosts + 1)] = self.addHost("h{}".format(number_of_hosts + 1))
        for i in range(number_of_hosts + 2, 2*number_of_hosts + 2):
            nodes["h{}".format(i)] = self.addHost("h{}".format(i))
        for i in range(number_of_hosts, number_of_hosts + number_of_hosts // 2):
            nodes["s{}".format(i)] = self.addSwitch("s{}".format(i))
        links = [("h{}".format(i), "s{}".format((i-1)//2 + 1)) for i in range(1, number_of_hosts + 1)]
        next_level = number_of_hosts // 2
        base = 0
        while next_level > 1:
            links = links + [("s{}".format(i+base), "s{}".format((i-1)//2 + 1 + next_level + base)) for i in range(1, next_level+1)]
            base += next_level
            next_level = next_level // 2
        # the load generator is connected to the switch that is the root of the tree
        links.append(("h{}".format(number_of_hosts + 1), "s{}".format(number_of_hosts - 1)))
        for i in range(1, number_of_hosts // 2 + 1):
            links.append(("s{}".format(i), "s{}".format(i + number_of_hosts - 1)))
        for i in range(number_of_hosts + 2, 2*number_of_hosts + 2):
            links.append(("h{}".format(i), "s{}".format((i-number_of_hosts-2)//2 + number_of_hosts)))
        # Add links -- don't touch this
        for pair in links:
            self.addLink(nodes[pair[0]], nodes[pair[1]])


class Tree_SUT_with_group_leader( Topo ):
    def __init__(self, depth):
        self.depth = depth
        Topo.__init__(self)

    def build( self ):
        "Create ETH topo."

        # Add hosts and switches -- from here you can change topology
        nodes = {}
        number_of_hosts = 2**self.depth
        for i in range(1, number_of_hosts + 1):
            nodes["h{}".format(i)] = self.addHost("h{}".format(i))
        for i in range(1, number_of_hosts):
            nodes["s{}".format(i)] = self.addSwitch("s{}".format(i))
        # I need a load generator separated from the observers, to not have problems with mininet commands
        nodes["h{}".format(number_of_hosts + 1)] = self.addHost("h{}".format(number_of_hosts + 1))
        for i in range(number_of_hosts + 2, 2*number_of_hosts + 2):
            nodes["h{}".format(i)] = self.addHost("h{}".format(i))
        for i in range(number_of_hosts, number_of_hosts + number_of_hosts // 2):
            nodes["s{}".format(i)] = self.addSwitch("s{}".format(i))
        links = [("h{}".format(i), "s{}".format((i-1)//2 + 1)) for i in range(1, number_of_hosts + 1)]
        # I also need a bootnode connected to the same switch of the load generator
        nodes["h{}".format(2*number_of_hosts + 2)] = self.addHost("h{}".format(2*number_of_hosts + 2))
        next_level = number_of_hosts // 2
        base = 0
        while next_level > 1:
            links = links + [("s{}".format(i+base), "s{}".format((i-1)//2 + 1 + next_level + base)) for i in range(1, next_level+1)]
            base += next_level
            next_level = next_level // 2
        # the load generator is connected to the switch that is the root of the tree
        links.append(("h{}".format(number_of_hosts + 1), "s{}".format(number_of_hosts - 1)))
        links.append(("h{}".format(2*number_of_hosts + 2), "s{}".format(number_of_hosts - 1)))
        for i in range(1, number_of_hosts // 2 + 1):
            links.append(("s{}".format(i), "s{}".format(i + number_of_hosts - 1)))
        for i in range(number_of_hosts + 2, 2*number_of_hosts + 2):
            links.append(("h{}".format(i), "s{}".format((i-number_of_hosts-2)//2 + number_of_hosts)))
        # Add links -- don't touch this
        for pair in links:
            self.addLink(nodes[pair[0]], nodes[pair[1]])


class StarTopo( Topo ):
    def __init__(self, number_of_hosts):
        self.number_of_hosts = number_of_hosts
        Topo.__init__(self)

    def build( self ):
        "Create ETH topo."

        # Add hosts and switches -- from here you can change topology
        nodes = {}
        for i in range(1, self.number_of_hosts + 1):
            nodes["h{}".format(i)] = self.addHost("h{}".format(i))
        nodes["s1"] = self.addSwitch("s1")

        # In 'links' I put host always as first element of the tuple to simplify the code for the creation of the sniffing dict.
        links = [("h{}".format(i), "s1") for i in range(1, self.number_of_hosts + 1)]
        # Add links -- don't touch this
        for pair in links:
            self.addLink(nodes[pair[0]], nodes[pair[1]])
