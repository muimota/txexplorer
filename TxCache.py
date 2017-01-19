import sqlite3
import requests
import grequests
from random import choice
from bitcoin import * #pip install bitcoin
from tqdm import tqdm


class TxCache:
    """cache to store and retrieve from different webservices tx"""

    BASE_URLS = (
                    'https://blockexplorer.com/api/rawtx/{}',
                    'http://btc.blockr.io/api/v1/tx/raw/{}',
                    'https://blockchain.info/rawtx/{}?format=hex',
                    'https://insight.bitpay.com/api/rawtx/{}',
                    'https://bitaps.com/api/raw/transaction/{}',
                    'https://api.smartbit.com.au/v1/blockchain/tx/{}/hex',
                    'https://chain.so/api/v2/get_tx/BTC/{}'
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

    def getMultiple(self,txids):

        #remove duplicates
        txids = set(txids)
        #check which ones are already in cache
        cachedtx = set()
        for txid in txids:
            self.cursor.execute('SELECT id from txcache WHERE id=?', (txid,))
            result = self.cursor.fetchone()
            if result != None:
                cachedtx.add(txid)

        pendingtx = txids - cachedtx
        print "cached: {} ".format(len(cachedtx))

        #http://stackoverflow.com/a/41271058/2205297
        maxconn = len(TxCache.BASE_URLS) * 5
        pendingtx = list(pendingtx)

        pbar = tqdm(total = len(txids),initial = len(cachedtx))

        #download transactions
        while len(pendingtx) > 0:


            #print "transaction explored:{} / {}".format(totalPending - len(pendingtx),totalPending)
            reqTxs = pendingtx[:maxconn]
            pendingtx = pendingtx[maxconn:]

            reqs   = []
            for txid in reqTxs:
                BASE_URL = choice(TxCache.BASE_URLS)
                txurl = BASE_URL.format(txid)
                req = grequests.get(txurl,timeout = 1.5)
                reqs.append(req)

            responses = grequests.map(reqs)
            exploredTx = 0
            for i in range(len(reqTxs)):
                r = responses[i]
                txid = reqTxs[i]
                try:
                    txraw = TxCache.parseWebResponse(r.text,txid)
                    self.put(txid,txraw)
                except Exception as e:
                    #TODO: check what kind it might be an unexisting tx
                    #print e
                    pendingtx.insert(0,txid)
                    continue
                exploredTx += 1
                self.put(txid,txraw)
            pbar.update(exploredTx)
        pbar.close()

    def put(self,txid,txraw):
        self.cursor.execute("INSERT OR IGNORE INTO txcache(id,txraw) VALUES(?,?)",(txid,txraw,))
        self.conn.commit()

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
    txid = '9873d0244d71b3358a04675e033d3405e48bfcfe7b65166c34f2942b1ca0e41f'
    print tc.get(txid,True)

    multipletx = [
        '681c54d9598ef6c7fa11bc84a9cabf2197cea684fa90a9f41eeca75473c8b367',
        'aa5d06f794515b7d7ed079fe882e1024e70400db1e5f775fe0d67cf8b48b6e9c'
    ]
    tc.getMultiple(multipletx)
