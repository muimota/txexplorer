import pyjsonrpc
from collections import Counter

class TxCache:

    def __init__(self):

        self.client     = pyjsonrpc.HttpClient(url='http://localhost:8332',username='bitcoin',password='local321')
        self.addresses  = {}
        self.reads   = Counter()
        self.blocks     = Counter()

    def get(self,txId):

        if txId not in self.addresses:
            tx = self.client.call('getrawtransaction',txId,1)            
            self.blocks[tx['blockhash']] += 1
            self.addresses[txId] = tx
    
        self.reads[txId] += 1

        return self.addresses[txId]
    
    def getFileId(self,txId):
        
        fileInfo = self.client.call('gettxdiskpos',txId)
        return "{}{}".format(fileInfo['nFile'],fileInfo['nPos'])
        

    def __repr__(self):
        reads = [read[1] for read in self.reads.most_common(5)]
        blocks = [block[1] for block in self.blocks.most_common(10)]
        desc = "addresses:{} blocks:{} top10:{} ".format(len(self.addresses),len(self.blocks),blocks)
        return desc

    def clear(self):
        del(self.addresses)
        self.addresses = {}

if __name__ == '__main__':
    from pprint import pprint
    tc = TxCache()
    txid = 'ead69a69fa2ee29793639aeb4753a9c9aed11d8b2291b45a3637d6149c2cdc30'
    pprint(tc.get(txid))
    pprint(tc.getFileId(txid))
    print tc
