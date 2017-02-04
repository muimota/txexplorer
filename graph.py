
from collections import Counter
from utils import *
from tqdm import tqdm
import cPickle as pickle
from pprint import pprint
from TxCache import TxCache
import bitcoin

tc = TxCache()

def getStepData(inputs, valueThreshold = 0):
    """checks inputs and returns stepdata with inputs (vout,txid)
    inputs[(vout,txid)] = value
    """
    stepInputs = Counter()
    addresses  = set()
    coinbases  = set()

    #get txids
    txIds = [input[1] for input in inputs]
    #remove duplicates
    txIds = list(set(txIds))
    
    fileIds = {}
    print "getting filepos:"
    for txId in tqdm(txIds):
        #print txId
        fileIds[txId] = tc.getFileId(txId)

    
    #sort txid by file
    #http://stackoverflow.com/a/7340031/2205297
    txIds = sorted(fileIds,key=fileIds.get)
    #print txIds
    #cache
    print 'getting raw'
    for txId in tqdm(txIds):
        tx = tc.get(txId,0)
       
    
    for txId in tqdm(txIds):

            
        tx = tc.get(txId,0)
        #pprint(tx)
        #take the first
        for output in tx['outs'][:1]:

            script = output['script'].encode('hex')
            value  = output['value']

	        #check is a valid transaction and parses address
            if script[:6] == '76a914' and script[-4:] == '88ac':
                addressId = bitcoin.hex_to_b58check(script[6:-4])
            #return back to the wallet
            elif script[:4] == 'a914' and script[-2:] == '87':
                addressId = bitcoin.hex_to_b58check(script[6:-4])
                #breakdown[address] += int(value * ratio)
            else:
                print 'no standard tx '
	            
            addresses.add(addressId)
        
        newInputs = breakdownInput(tx,None)
         #falta anadir addressId
        txinputs =  [txinput[1] for txinput in newInputs.keys()]

        if '0'*64 in txinputs:
            coinbases.add(addressId)
            continue
       
        stepInputs += newInputs
      
    stepdata = {'inputs':stepInputs,'addresses':addresses,'coinbases':coinbases}
    return stepdata
    

def exploreTransaction(txId,stepCount = 50,valueThreshold = 0):

    data_folder = 'data/'
    filename    = 'tx_{}'.format(txId[-5:])
    resetPickle = False

    try:
        if resetPickle:
            raise Exception()
        data = pickle.load(open(data_folder+filename+'.pickle','rb'))
        #recalculate last 2 steps in case last is corrupted
        inputs = data['stepdata'][-1]['inputs']
    except Exception as e:
        print '{} file not found!'.format(filename)
        data = {}
        data['transactionId'] = txId
        data['stepdata'] = []

        tx = tc.get(txId,0)
       
        pprint(tx)
        inputs = breakdownInput(tx)


    startStep = len(data['stepdata'])-1
    if startStep > 0:
        print 'startStep:{}'.format(startStep)
    unsavedInputsCount = 0 #

    for step in range(startStep,stepCount):
    
        tc.clear()
        stepdata  = getStepData(inputs,valueThreshold)
    
        coinbases = stepdata['coinbases']
        addresses = stepdata['addresses']
        inputs    = stepdata['inputs']
        data['stepdata'].append(stepdata)

        unsavedInputsCount += len(inputs)
        #save after number of unsaved inputs when end or number of stepsis reached
        if unsavedInputsCount > 10000 or len(inputs) == 0 or step == stepCount - 1:
            pickle.dump(data,open(data_folder+filename+'.pickle','wb'))
            unsavedInputsCount = 0

        if len(inputs) == 0:
            break

        print tc

        sumValue = sum(inputs.values())

        print "step:{} inputs:{} sumValue:{} (mean:{}) addresses:{} coinbases:{}".format(step,len(inputs),sumValue,sumValue/float(len(inputs.values())),len(addresses),len(coinbases))
   
    print 'saving...'
    convertJson(data,open(data_folder+filename+'.json','wb'))


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
