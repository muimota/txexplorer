
from collections import Counter
from utils import *
import cPickle as pickle
#devuelve


def getStepData(inputs):

    stepInputs = Counter()
    addresses = set()
    coinbase  = set()

    for input in inputs:

        addressId,txId = input
        value          = inputs[input]

        tx = getTransaction(txId)
        if 'isCoinBase' in tx:
            coinbase.add(addressId)
            continue

        newInputs = breakdownInput(tx,addressId,value)
        for newInput in newInputs:
            addressId,txId = newInput
            addresses.add(addressId)
        #aqui
        stepInputs += newInputs

    stepdata = {'inputs':stepInputs,'addresses':addresses,'coinbase':coinbase}
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
    inputs = breakdownInput(tx)
    for step in range(startStep,50):

        stepdata  = getStepData(inputs)
        coinbase  = stepdata['coinbase']
        addresses = stepdata['addresses']
        inputs    = stepdata['inputs']

        data['stepdata'].append(stepdata)
        pickle.dump(data,open(filename,'wb'))

        print "step:{} inputs:{} sumValue:{} address:{} coinbase:{}".format(step,len(inputs),sum(inputs.values()),len(addresses),len(coinbase))

        if len(inputs) == 0:
            break
