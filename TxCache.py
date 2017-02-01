import sqlite3
import requests
from random import choice
import pyjsonrpc

class TxCache:

    def __init__(self):

        self.client     = pyjsonrpc.HttpClient(url='http://localhost:18332',username='bitcoin',password='local321')
        self.addresses  = {}


    def get(self,txId):

        if txId not in self.addresses:
            tx = self.client.call('getrawtransaction',txId,1)
            self.addresses[txId] = tx

        return self.addresses[txId]

if __name__ == '__main__':
    from pprint import pprint
    tc = TxCache()
    txid = '469b8ac0d50a5d7ca2f38a6aae0dc18362d45f9323cb5d828c1b190edb713e96'
    pprint(tc.get(txid))
