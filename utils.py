import requests
import cPickle as pickle
import json
from collections import Counter
from TxCache import TxCache
from pprint import pprint
import math

tc = TxCache()

def convSatoshi(btc):
    """ BTC to Satoshi Conversion """
    return long(math.ceil(float(btc) * 100000000))

def getTransaction(txId):
    """Get a parsed Tx from a insight API"""
    tx = tc.get(txId)
    return tx


def breakdownInput(tx,value = None):
    """Breakdowns inputs in a transaction returns {vout:balance}"""
    inputAddresesId = Counter()
	
    for input in tx['ins']:
		outpoint = input['outpoint']
		inputAddresesId[(outpoint['index'],outpoint['hash'].encode('hex'))] += 1

    return inputAddresesId

def convertJson(data,f = None):
    """ Converts data so it can be stored in a json file
    -- data dict with txId, stepdata
    -- f file handler to write, if no defined return json"""

    data = data.copy()

    for stepdata in data['stepdata']:

        inputsCounter = Counter()
        
        if 'inputs' in stepdata:
            inputs        = stepdata['inputs']
            for key in inputs:
                inputsCounter[key[0]] += inputs[key]
            #delete 'unparsed data' transactions
            del(inputsCounter[None])
        stepdata['inputs']    = dict(inputsCounter)
        stepdata['addresses'] = list(stepdata['addresses'])
        #delete addresses sin this data is already stored in inputsCounter
        stepdata['coinbases'] = list(stepdata['coinbases'])

    if f != None:
        json.dump(data,f)

if __name__ == '__main__':

    tx = getTransaction('457487dc5acac1775d4c4806ded2402188016b0be2c209a7c6611aa0a7facc1a')
    pprint(tx)

    inputs = breakdownInput(tx)
    print inputs
