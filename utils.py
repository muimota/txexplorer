import requests
import cPickle as pickle
import json
from collections import Counter
from TxCache import TxCache

BASE_URL = 'http://localhost:3001/insight-api/'
tc = TxCache()

def convSatoshi(btc):
    """ BTC to Satoshi Conversion """
    return long(float(btc) * 100000000)

def getTransaction(txId):
    """Get a parsed Tx from a insight API"""
    tx = tc.get(txId)
    return tx


def breakdownInput(tx,value = None):
    """Breakdowns inputs in a transaction returns {addr:balance}"""
    inputAddresesId = Counter()

    if value != None:
        ratio = float(value) / convSatoshi(tx['valueIn'])
    else:
        ratio  = 1.0

    if ratio == 0:
        raise Exception("ratio = 0")

    for input in tx['vin']:
        inputAddresesId[(input['addr'],input['txid'])] += convSatoshi(input['value'] * ratio)

    return inputAddresesId

def convertJson(data,f = None):
    """ Converts data so it can be stored in a json file
    -- data dict with txId, stepdata
    -- f file handler to write, if no defined return json"""

    data = data.copy()

    for stepdata in data['stepdata']:

        inputsCounter = Counter()
        inputs        = stepdata['inputs']
        for key in inputs:
            inputsCounter[key[0]] += inputs[key]
        #delete 'unparsed data' transactions
        #TODO:add an example of a
        del(inputsCounter[None])
        del(stepdata['addresses'])
        #delete addresses sin this data is already stored in inputsCounter
        stepdata['inputs']    = dict(inputsCounter)
        stepdata['coinbases'] = list(stepdata['coinbases'])

    if f != None:
        json.dump(data,f)

if __name__ == '__main__':
    #some tests
    filename = 'tx_94ca9'
    data = pickle.load(open(filename+'.pickle','rb'))
    convertJson(data,open(filename+'.json','wb'))
