import requests
import cPickle as pickle
import json
from collections import Counter


BASE_URL = 'http://localhost:3001/insight-api/'

def convSatoshi(btc):
    return int(float(btc) * 100000000)

def getTransaction(txId):
    r = requests.get(BASE_URL+'tx/'+txId)
    tx = r.json()
    return tx


def breakdownInput(tx,addressId=None,value = None):

    inputAddresesId = Counter()
    ratio  = 1.0
    if value != None:
        ratio = float(value) / convSatoshi(tx['valueOut'])

    for input in tx['vin']:
        inputAddresesId[(input['addr'],input['txid'])] += convSatoshi(input['value'] * ratio)

    return inputAddresesId

def convertJson(data,f = None):
    """ converts data so it can be stored in a json file
    -- data dict with txId, stepdata
    -- f file handler to write, if no defined return json"""

    data = data.copy()

    for stepdata in data['stepdata']:
        
        del(stepdata['inputs'])
        for key in ('addresses','coinbases'):
            stepdata[key] = list(stepdata[key])

    if f != None:
        json.dump(data,f)

if __name__ == '__main__':

    filename = 'tx_0b252'
    data = pickle.load(open(filename+'.pickle','rb'))
    convertJson(data,open(filename+'.json','wb'))
