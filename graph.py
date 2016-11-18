import requests
from collections import Counter
#devuelve
BASE_URL = 'http://localhost:3001/insight-api/'

def convSatoshi(btc):
    return int(float(btc) * 100000000)

def getTransaction(txId):
    r = requests.get(BASE_URL+'tx/'+txId)
    tx = r.json()
    return tx


def breakdownInputsAddresses(tx):

    inputValues = Counter()

    for input in tx['vin']:
        inputValues[input['addr']] += convSatoshi(input['value'])

    for output in tx['vout']:
        #very unlely to have more than one address
        #http://bitcoin.stackexchange.com/a/11311
        addresses = output['scriptPubKey']['addresses']
        inputValues[addresses[0]] -= convSatoshi(output['value'])

    #http://stackoverflow.com/a/16589453/2205297
    # get rid of negative addresses
    #inputValues = {addr:value for addr,value in inputValues.iteritems() if value > 0}

    return inputValues

def breakdownInputs(tx,value = None):

    if 'coinbase' in tx['vin'][0]:
        return None


    inputs = dict()
    feePerInput = convSatoshi(tx['fees'])/len(tx['vin'])
    ratio  = 1.0

    if value != None:
        ratio = float(value) / convSatoshi(tx['valueOut'])


    for input in tx['vin']:
        inputs[(input['addr'],input['txid'] )] = int((convSatoshi(input['value']))*ratio)

    return inputs

if __name__ == '__main__':
    txId = 'a0b8f0c42ccfd63c7a6ab03df848941e4a281ca15443a6120c4ed3db668f4ffa'
    tx = getTransaction(txId)

    print breakdownInputs(tx)
