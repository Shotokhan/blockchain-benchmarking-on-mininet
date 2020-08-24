from threading import Thread
import json
import time
from util_for_blockchain import hostToIp
from random import randint


class observingClient(Thread):
    def __init__(self, observingTime, observingHost, observedNet, observedHost):
        Thread.__init__(self)
        self.currentHeight = 0
        self.TX_count = 0
        self.observingTime = observingTime
        self.observingHost = observingHost
        self.observedNet = observedNet
        self.observedHost = observedHost

    def run(self):
        target = "http://{}:8501".format(hostToIp(self.observedHost))
        interact_json = lambda method,params : json.dumps({"jsonrpc":"2.0", "method":method, "params":params, "id":randint(10,1000)})
        interaction = """curl -m 2 -X POST -H "Content-Type: application/json" --data '{}' """ + target
        try:
            blockchainStatus = self.observedNet.nameToNode[self.observingHost].cmd(interaction.format(interact_json("eth_blockNumber", [])))
        except:
            pass
        grep_json = lambda s: s[s.find('{'):(s.rfind('}')+1)]
        blockchainStatus = grep_json(blockchainStatus)
        try:
            parsedBlockchainData = json.loads(blockchainStatus)
        except ValueError:
            parsedBlockchainData = {'result': hex(self.currentHeight)}
        try:
            self.currentHeight = int(parsedBlockchainData['result'], 16)
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
                    blockchainStatus = grep_json(self.observedNet.nameToNode[self.observingHost].cmd(interaction.format(interact_json("eth_blockNumber", []))))
                except:
                    pass
                try:
                    parsedBlockchainData = json.loads(blockchainStatus)
                except ValueError:
                    parsedBlockchainData = {'result': hex(self.currentHeight)}
                try:
                    phasedHeight = int(parsedBlockchainData['result'], 16)
                except:
                    phasedHeight = self.currentHeight
                elapsed = time.time() - start
                if elapsed >= self.observingTime:
                    break
            while self.currentHeight < phasedHeight:
                post_cmd = interaction.format(interact_json("eth_getBlockByNumber", [hex(self.currentHeight), False]))
                try:
                    blockData = grep_json(self.observedNet.nameToNode[self.observingHost].cmd(post_cmd))
                except:
                    pass
                try:
                    parsedBlockData = json.loads(blockData)
                #except ValueError:
                #    parsedBlockData = {'numberOfTransactions': 0}
                #try:
                    self.TX_count += len(parsedBlockData['result']['transactions'])
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
