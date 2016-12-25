
from collections import Counter
from utils import *
from tqdm import tqdm
import cPickle as pickle
#devuelve


def getStepData(inputs, valueThreshold = 0):
    """checks inputs and resturns stepdata with inputs (addr,txId)"""
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

def exploreTransaction(txId,stepCount = 50,valueThreshold = 0):

    filename = 'tx_{}'.format(txId[-5:])
    resetPickle = False

    try:
        if resetPickle:
            raise Exception()
        data = pickle.load(open(filename+'.pickle','rb'))
        #recalculate last 2 steps in case last is corrupted
        inputs = data['stepdata'][-1]['inputs']
    except Exception as e:
        print '{} file not found!'.format(filename)
        data = {}
        data['transactionId'] = txId
        data['stepdata'] = []
        tx = getTransaction(txId)
        inputs = breakdownInput(tx)

    startStep = len(data['stepdata'])-1
    if startStep > 0:
        print 'startStep:{}'.format(startStep)
    unsavedInputsCount = 0 #
    for step in range(startStep,stepCount):

        try:
            stepdata  = getStepData(inputs,valueThreshold)
        except:
            print 'error'
            break

        coinbases = stepdata['coinbases']
        addresses = stepdata['addresses']
        inputs    = stepdata['inputs']
        data['stepdata'].append(stepdata)

        unsavedInputsCount += len(inputs)
        #save after number of unsaved inputs when end or number of stepsis reached
        if unsavedInputsCount > 10000 or len(inputs) == 0 or step == stepCount - 1:
            pickle.dump(data,open(filename+'.pickle','wb'))
            unsavedInputsCount = 0

        if len(inputs) == 0:
            break

        sumValue = sum(inputs.values())

        print "step:{} inputs:{} sumValue:{} (mean:{}) addresses:{} coinbases:{}".format(step,len(inputs),sumValue,sumValue/float(len(inputs.values())),len(addresses),len(coinbases))

    print 'saving...'
    convertJson(data,open(filename+'.json','wb'))


if __name__ == '__main__':
    import argparse,utils
    utils.BASE_URL = 'https://insight.bitpay.com/api/'
    parser = argparse.ArgumentParser(description='Explores a bitcoin transaction')
    parser.add_argument('txId', metavar='txId', type=str, help='transaction hash to explore')
    parser.add_argument('-stepCount', metavar='steps', type=int, nargs='?', help='number of steps to explore')
    parser.add_argument('-valueThreshold', metavar='value', type=int, nargs='?', help='value threshold of input to explore')


    args = parser.parse_args()
    args = vars(args)

    stepCount = args['stepCount'] or  50
    valueThreshold = args['valueThreshold'] or 0
    txId = args['txId']

    exploreTransaction(txId,stepCount,valueThreshold)
