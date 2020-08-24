from threading import Thread
import json
import time
from util_for_blockchain import hostToIp


class observingClient(Thread):
    def __init__(self, observingTime, observingHost, observedNet, observedHost):
        Thread.__init__(self)
        self.currentHeight = None
        self.TX_count = 0
        self.observingTime = observingTime
        self.observingHost = observingHost
        self.observedNet = observedNet
        self.observedHost = observedHost

    def run(self):
        base_cmd = "curl -m 2 http://{}:6876/nxt?requestType=".format(hostToIp(self.observedHost))
        try:
            blockchainStatus = self.observedNet.nameToNode[self.observingHost].cmd("{}getBlockchainStatus".format(base_cmd))
        except:
            pass
        # I need it because the host also runs a NXT node so it has more output than needed
        grep_json = lambda s: s[s.find('{'):(s.rfind('}')+1)]
        blockchainStatus = grep_json(blockchainStatus)
        try:
            parsedBlockchainData = json.loads(blockchainStatus)
        except ValueError:
            parsedBlockchainData = {'numberOfBlocks': self.currentHeight}
        try:
            self.currentHeight = parsedBlockchainData['numberOfBlocks']
        except:
            pass
        phasedHeight = self.currentHeight
        # this sleep is to somewhat synchronize observing clients among them and with the generation of transactions
        time.sleep(1)
        start = time.time()
        elapsed = time.time() - start
        # polling
        while elapsed < self.observingTime:
            while self.currentHeight == phasedHeight:
                time.sleep(1)
                try:
                    blockchainStatus = grep_json(self.observedNet.nameToNode[self.observingHost].cmd("{}getBlockchainStatus".format(base_cmd)))
                except:
                    pass
                try:
                    parsedBlockchainData = json.loads(blockchainStatus)
                except ValueError:
                    parsedBlockchainData = {'numberOfBlocks': self.currentHeight}
                try:
                    phasedHeight = parsedBlockchainData['numberOfBlocks']
                except:
                    phasedHeight = self.currentHeight
                if self.currentHeight is None:
                    self.currentHeight = phasedHeight
                elapsed = time.time() - start
                if elapsed >= self.observingTime:
                    break
            while self.currentHeight < phasedHeight:
                post_cmd = "curl -m 2 --data 'includeTransactions=False&height={}' {}getBlock".format(self.currentHeight, base_cmd[10:])
                try:
                    blockData = grep_json(self.observedNet.nameToNode[self.observingHost].cmd(post_cmd))
                except:
                    pass
                try:
                    parsedBlockData = json.loads(blockData)
                #except ValueError:
                #    parsedBlockData = {'numberOfTransactions': 0}
                #try:
                    self.TX_count += parsedBlockData['numberOfTransactions']
                    self.currentHeight += 1
                    print("{}: cumulative TX count = {}, height = {}".format(self.observedHost, self.TX_count, self.currentHeight))
                except:
                    pass
                elapsed = time.time() - start
                if elapsed >= self.observingTime:
                    break
            elapsed = time.time() - start

    def TPS(self):
        return float(self.TX_count) / float(self.observingTime) 
