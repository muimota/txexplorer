import sqlite3
import requests
from random import choice
from bitcoin import *


class TxCache:
    """cache to store and retrieve from different webservices tx"""

    BASE_URLS = (
                    'https://blockexplorer.com/api/rawtx/{}',
                    'http://btc.blockr.io/api/v1/tx/raw/{}',
                    'https://blockchain.info/rawtx/{}?format=hex',
                    'https://insight.bitpay.com/api/rawtx/{}',
                    'https://bitaps.com/api/raw/transaction/{}'
                )

    @staticmethod
    def parseWebResponse(webresponse,txid = None):
        """returns a txraw from webresponse optionally checks is correct"""
        startIndex = webresponse.find('"01000000')

        if startIndex > -1:
            endIndex = webresponse.find('"',startIndex+1)
            txraw = webresponse[(startIndex+1):endIndex]

        else:
            txraw = webresponse

        if txid != None:
            try:
                hash = txhash(txraw.decode('hex'))
            except:
                raise Exception('tx not found!')
            if txid != hash:
                raise Exception('tx hash failed!')

        return txraw


    def __init__(self,filename='txcache.db'):
        """contructor, filename parameter will be where database will be stored"""

        self.conn = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()

        # Create table
        #@TODO use a blob field size should be half
        self.cursor.execute('''CREATE TABLE if not exists txcache (id text UNIQUE, txraw text)''')


    def get(self,txid,parsed = False):

        self.cursor.execute('SELECT txraw from txcache WHERE id=?', (txid,))
        txraw = self.cursor.fetchone()

        if(txraw == None):
            #pick random provider
            BASE_URL = choice(TxCache.BASE_URLS)
            txurl = BASE_URL.format(txid)
            r  = requests.get(txurl)
            #print r.headers.get('content-type')
            try:
                txraw = TxCache.parseWebResponse(r.text,txid)
            except Exception as e:
                print txurl
                raise e
            self.cursor.execute("INSERT INTO txcache(id,txraw) VALUES(?,?)",(txid,txraw,))
            self.conn.commit()
            txraw = (txraw,)

        if parsed:
            tx = deserialize(txraw[0].decode('hex'))
        else:
            tx = txraw[0]
        return tx

if __name__ == '__main__':
    tc = TxCache()
    txid = '681c54d9598ef6c7fa11bc84a9cabf2197cea684fa90a9f41eeca75473c8b367'
    print tc.get(txid,True)
