import sqlite3
import requests
from random import choice
import json


class TxCache:

    def __init__(self,filename='txcache.db',url='http://localhost:3001/insight-api/tx/{}'):

        self.conn   = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()
        self.url    = url
        # Create table
        #@TODO use a blob field size should be half
        self.cursor.execute('''CREATE TABLE if not exists txcache (id text UNIQUE, txraw text)''')


    def get(self,txid,parsed = False):

        self.cursor.execute('SELECT txraw from txcache WHERE id=?', (txid,))
        txjson = self.cursor.fetchone()

        if(txjson == None):
            #pick random provider

            txurl = self.url.format(txid)
            r  = requests.get(txurl)
            tx = r.json()
            self.cursor.execute("INSERT INTO txcache(id,txraw) VALUES(?,?)",(txid,json.dumps(tx,separators=(',', ': '))))
            self.conn.commit()
        else:
            tx = json.loads(txjson[0])

        return tx

if __name__ == '__main__':
    from pprint import pprint
    tc = TxCache()
    txid = '469b8ac0d50a5d7ca2f38a6aae0dc18362d45f9323cb5d828c1b190edb713e96'
    pprint(tc.get(txid))
