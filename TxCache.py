import pyjsonrpc
from collections import Counter

class TxCache:

    def __init__(self):

        self.client     = pyjsonrpc.HttpClient(url='http://localhost:8332',username='bitcoin',password='local321')
        self.addresses  = {}
	self.accesses   = Counter()

    def get(self,txId):

        if txId not in self.addresses:
            tx = self.client.call('getrawtransaction',txId,1)
            self.addresses[txId] = tx
	
	self.accesses[txId] += 1

        return self.addresses[txId]

    def __repr__(self):
        desc = "size:{} caches:{}".format(len(self.addresses),sum(self.accesses.values()))
        return desc

    def clear(self):
        del(self.addresses)
	self.addresses = {}

if __name__ == '__main__':
    from pprint import pprint
    tc = TxCache()
    txid = '469b8ac0d50a5d7ca2f38a6aae0dc18362d45f9323cb5d828c1b190edb713e96'
    pprint(tc.get(txid))
    print tc
