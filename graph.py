
from collections import Counter
from utils import *
from tqdm import tqdm
import cPickle as pickle
#devuelve


def getStepData(inputs, valueThreshold = 0):

    stepInputs = Counter()
    addresses  = set()
    coinbases  = set()

    for input in tqdm(inputs):

        addressId,txId = input
        value          = inputs[input]

        if value < valueThreshold:
            continue

        tx = getTransaction(txId)

        if 'isCoinBase' in tx:
            if addressId == None:
                continue
            coinbases.add(addressId)
            continue

        newInputs = breakdownInput(tx,addressId,value)
        #print '>{} >{}'.format(txId,addressId)
        for newInput in newInputs:

            addressId,txId = newInput
            #cases where is not parsed corectly like b039d4a15f5b8e10bcec5384da8995f134fb75e1e1da81e82d25c800e224fa16
            if addressId == None:
                continue
            addresses.add(addressId)
        #aqui
        stepInputs += newInputs

    stepdata = {'inputs':stepInputs,'addresses':addresses,'coinbases':coinbases}
    return stepdata

if __name__ == '__main__':

    txId = '0142811d0421e0bb0ac2f0ca17c0034e9072f3dbae26cb8cbb5f660970f8df6a'
    filename = 'tx_{}'.format(txId[-5:])
    resetPickle = False

    try:
        if resetPickle:
            raise Exception()
        data = pickle.load(open(filename+'.pickle','rb'))
        #recalculate last 2 steps in case last is corrupted
        inputs = data['stepdata'][-1]['inputs']
    except Exception as e:
        print e
        print '{} file not found!'.format(filename)
        data = {}
        data['transactionId'] = txId
        data['stepdata'] = []
        tx = getTransaction(txId)
        inputs = breakdownInput(tx)

    startStep = len(data['stepdata'])-1
    print 'startStep:{}'.format(startStep)

    for step in range(startStep,50):

        stepdata  = getStepData(inputs,None)
        coinbases = stepdata['coinbases']
        addresses = stepdata['addresses']
        inputs    = stepdata['inputs']

        data['stepdata'].append(stepdata)
        if step % 10 == 0:
            pickle.dump(data,open(filename+'.pickle','wb'))
        sumValue = sum(inputs.values())
        if len(inputs) == 0:
            break

        print "step:{} inputs:{} sumValue:{} (mean:{}) addresses:{} coinbases:{}".format(step,len(inputs),sumValue,sumValue/float(len(inputs.values())),len(addresses),len(coinbases))


    print 'saving...'
    convertJson(data,open(filename+'.json','wb'))
