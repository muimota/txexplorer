import requests
from collections import Counter
import cPickle as pickle
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

def getStepData(inputTxs):

    stepTxs = Counter()
    addresses = set()
    coinbase  = set()

    for txId in inputTxs:

        tx = getTransaction(txId)
        if 'isCoinBase' in tx:
            #print tx
            for output in tx['vout']:
                scriptPubKey = output['scriptPubKey']
                if 'addresses' in  output['scriptPubKey']:
                    coinbase = coinbase.union(output['scriptPubKey']['addresses'])
                else:
                    print 'no address found {}'.format(txId)
            continue

        for input in tx['vin']:
            addresses.add(input['addr'])
        stepTxs += breakdownInputTxs(tx,inputTxs[txId])

    stepdata = {'inputTxs':stepTxs,'addresses':addresses,'coinbase':coinbase}
    return stepdata

if __name__ == '__main__':
    txId = '23fae8e2913669fd76c0f1ac5fe9a1e50b2c857cc317937edb2b2d3dfcf0b252'
    filename = 'tx_{}.pickle'.format(txId[-5:])
    resetPickle = False

    try:
        if resetPickle:
            raise Exception()

        data = pickle.load(open(filename,'rb'))
    except:
        print '{} file not found!'.format(filename)
        data = {}
        data['transactionId'] = txId
        data['stepdata'] = []

    startStep = len(data['stepdata'])
    print 'startStep:{}'.format(startStep)


    tx = getTransaction(txId)
    inputTxs = breakdownInputTxs(tx)

    for step in range(startStep,50):

        stepdata  = getStepData(inputTxs)
        coinbase  = stepdata['coinbase']
        addresses = stepdata['addresses']
        inputTxs  = stepdata['inputTxs']

        data['stepdata'].append(stepdata)
        pickle.dump(data,open(filename,'wb'))

        print "step:{} tx:{} sumValue:{} address:{} coinbase:{}".format(step,len(inputTxs),sum(inputTxs.values()),len(addresses),len(coinbase))

        if len(inputTxs) == 0:
            break
