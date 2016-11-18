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


def breakdownInputTxs(tx,value = None):


    inputTxs = Counter()
    ratio  = 1.0
    if value != None:
        ratio = float(value) / convSatoshi(tx['valueOut'])

    for input in tx['vin']:
        inputTxs[input['txid']] += convSatoshi(input['value'] * ratio)

    return inputTxs

def breakdownInputs(tx,value = None):

    if 'isCoinBase' in tx:
        print 'coinbase!'
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
    txId = '39173edcabb500b883e8a02f33a13b629b9b3e55b14008eb7c2d18c58060d02c'
    tx = getTransaction(txId)

    inputTxs = breakdownInputTxs(tx)
    for step in range(2000):

        stepTx = Counter()
        addresses = set()
        coinbase  = set()
        for txId in inputTxs:

            tx = getTransaction(txId)
            if 'isCoinBase' in tx:
                #print tx
                address = tx['vout'][0]['scriptPubKey']['addresses'][0]
                #print 'coinbaseAddr> {}'.format(address)
                coinbase.add(address)
                continue

            for input in tx['vin']:
                addresses.add(input['addr'])
            stepTx += breakdownInputTxs(tx,inputTxs[txId])
        inputTxs = stepTx
        print "step:{} tx:{} sumValue:{} address:{} coinbase:{}".format(step,len(inputTxs),sum(inputTxs.values()),len(addresses),len(coinbase))
        if len(inputTxs) == 0:
            break
