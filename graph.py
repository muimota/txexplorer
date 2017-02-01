
from collections import Counter
from utils import *
from tqdm import tqdm
import cPickle as pickle
from pprint import pprint
#devuelve


def getStepData(inputs, valueThreshold = 0):
    """checks inputs and returns stepdata with inputs (vout,txid)
    inputs[(vout,txid)] = value
    """
    stepInputs = Counter()
    addresses  = set()
    coinbases  = set()

    for input in tqdm(inputs):

        vout,txId   = input
        value       = inputs[input]

        if value < valueThreshold:
            continue

        tx = getTransaction(txId)

        addressId = tx['vout'][vout]['scriptPubKey']['addresses'][0]

        if 'coinbase' in tx['vin'][0]:
            #print 'coinbase!!'
            coinbases.add(addressId)
            continue
        else:
            addresses.add(addressId)

        newInputs = breakdownInput(tx,value)

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

        stepdata  = getStepData(inputs,valueThreshold)

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

        #pprint(inputs)

        sumValue = sum(inputs.values())

        print "step:{} inputs:{} sumValue:{} (mean:{}) addresses:{} coinbases:{}".format(step,len(inputs),sumValue,sumValue/float(len(inputs.values())),len(addresses),len(coinbases))

    print 'saving...'
    convertJson(data,open(filename+'.json','wb'))


if __name__ == '__main__':
    import argparse,utils
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
