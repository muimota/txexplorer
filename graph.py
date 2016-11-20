
from collections import Counter
from utils import *
from tqdm import tqdm
import cPickle as pickle
#devuelve


def getStepData(inputs):

    stepInputs = Counter()
    addresses  = set()
    coinbases  = set()

    for input in tqdm(inputs):

        addressId,txId = input
        value          = inputs[input]

        tx = getTransaction(txId)
        if 'isCoinBase' in tx:
            coinbases.add(addressId)
            continue

        newInputs = breakdownInput(tx,addressId,value)
        #print '>{} >{}'.format(txId,addressId)
        for newInput in newInputs:
            if newInput == None:
                continue
            addressId,txId = newInput
            addresses.add(addressId)
        #aqui
        stepInputs += newInputs

    stepdata = {'inputs':stepInputs,'addresses':addresses,'coinbases':coinbases}
    return stepdata

if __name__ == '__main__':

    txId = '23fae8e2913669fd76c0f1ac5fe9a1e50b2c857cc317937edb2b2d3dfcf0b252'
    filename = 'tx_{}.pickle'.format(txId[-5:])
    resetPickle = True

    try:
        if resetPickle:
            raise Exception()
        data = pickle.load(open(filename,'rb'))
        #recalculate last 2 steps in case last is corrupted
        inputs = data['stepdata'][-2]['inputs']
    except Exception as e:
        print e
        print '{} file not found!'.format(filename)
        data = {}
        data['transactionId'] = txId
        data['stepdata'] = []
        tx = getTransaction(txId)
        inputs = breakdownInput(tx)

    startStep = len(data['stepdata'])
    print 'startStep:{}'.format(startStep)

    for step in range(startStep,3):

        stepdata  = getStepData(inputs)
        coinbases = stepdata['coinbases']
        addresses = stepdata['addresses']
        inputs    = stepdata['inputs']

        data['stepdata'].append(stepdata)
        pickle.dump(data,open(filename,'wb'))

        print "step:{} inputs:{} sumValue:{} addresses:{} coinbases:{}".format(step,len(inputs),sum(inputs.values()),len(addresses),len(coinbases))

        if len(inputs) == 0:
            break
