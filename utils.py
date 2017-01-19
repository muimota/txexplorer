import requests
import cPickle as pickle
import json

from collections import Counter
from bitcoin import *




BASE_URL = 'https://blockchain.info/rawtx/{}?format=hex'

def getTransaction(txId):
    """Get a parsed Tx from a insight API"""
    r = requests.get(BASE_URL.format(txId))
    tx = deserialize(r.text.decode('hex'))
    return tx

def getInputs(tx):
    """returns tx inputs [(txid,outindex)]  """
    inputs = []
    for input in tx['ins']:
        outpoint = input['outpoint']
        inputs.append([outpoint['hash'].encode('hex'),outpoint['index']])

    return inputs

def getInputRatio(tx,outputIndex):
    """returns ratio of and outIndex of the total amount in the transaction"""
    outValue = tx['outs'][outputIndex]['value']
    totalOutValue = 0.0
    for output in tx['outs']:
        totalOutValue += output['value']

    return outValue/float(totalOutValue)

def getOutputs(tx,outputIndex = None,ratio = 1.0):
    """returns {address:value} """
    breakdown = Counter()
    outputs = tx['outs']

    if outputIndex != None:
        outputs = (tx['outs'][outputIndex],)

    for output in outputs:
        script = output['script'].encode('hex')
        value  = output['value']

        #check is a valid transaction and parses address
        if script[:6] == '76a914' and script[-4:] == '88ac':
            address = hex_to_b58check(script[6:-4])
            breakdown[address] += int(value * ratio)
        #return to the wallet
        elif script[:4] == 'a914' and script[-2:] == '87':
            address = hex_to_b58check(script[6:-4])
            breakdown[address] += int(value * ratio)
        else:
            print script
            raise Exception("fuck!")

    return breakdown


def convertJson(data,f = None):
    """ Converts data so it can be stored in a json file
    -- data dict with txId, stepdata
    -- f file handler to write, if no defined return json"""

    data = data.copy()

    for stepdata in data['stepdata']:

        inputsCounter = Counter()
        inputs        = stepdata['inputs']
        for key in inputs:
            inputsCounter[key[0]] += inputs[key]
        #delete 'unparsed data' transactions
        #TODO:add an example of a
        del(inputsCounter[None])
        del(stepdata['addresses'])
        #delete addresses sin this data is already stored in inputsCounter
        stepdata['inputs']    = dict(inputsCounter)
        stepdata['coinbases'] = list(stepdata['coinbases'])

    if f != None:
        json.dump(data,f)

if __name__ == '__main__':
    from pprint import pprint
    from TxCache import TxCache

    tc  = TxCache()
    txid = '44a8eb724f95cafd132b1222ba43c610492009a1d0889f9588ecadad7e45484a'
    tx = tc.get(txid,True)
    #generate a raw transaction from the parsed
    txraw = serialize(tx)
    print txhash(txraw)
    pprint(tx)
    print getOutputs(tx)

    scaledInputs = [[1.0,getInputs(tx)]]

    for i in range(20):
        outputs = Counter()
        nextInputs = []


        txs = set()
        for scaledInput in scaledInputs:
            #print scaledInput
            ratio,inputs = scaledInput
            for input in inputs:
                txid     = input[0]
                outindex = input[1]

                #check if a tx is a coinbase transaction
                if txid != '0'*64:
                    txs.add(txid)

        print "total txs:{}".format(len(txs))
        print "step:{}".format(i)
        tc.getMultiple(txs)

        for scaledInput in scaledInputs:
            #print scaledInput
            ratio,inputs = scaledInput
            for input in inputs:
                txid     = input[0]
                outindex = input[1]

                #check if a tx is a coinbase transaction
                if txid == '0'*64:
                    print '>>>>>coinbase!'
                    continue
                while True:
                    try:
                        tx = tc.get(txid,True)
                        break
                    except Exception as e:
                        print '>>>'+txid


                ratio *= getInputRatio(tx,outindex)
                nextInputs.append((ratio,getInputs(tx)))
                outputs += getOutputs(tx,outindex,ratio)

        scaledInputs = nextInputs
            #print scaledInputs
        #pprint(dict(outputs))
        print "step:{} addreses:{} sum:{}".format(i,len(outputs), sum(outputs.itervalues()))

        #pprint(dict(outputs))

        #pprint(inputs)
