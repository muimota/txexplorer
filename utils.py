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
    if outputIndex != None and outputIndex in tx['outs']:
        breakdown = Counter()

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
    txid = '2c837541dcaff50e6573af05d2964112366798865a4f8d411380dfd92168694a'
    tx = getTransaction(txid)
    #generate a raw transaction from the parsed
    txraw = serialize(tx)
    print txraw
    pprint(tx)
    print txhash(txraw)
    print getOutputs(tx)

    inputs = getInputs(tx)
    for i in range(13):
        outputs = Counter()
        nextInputs = []
        for input in inputs:
            txid     = input[0]
            outindex = input[1]
            if txid == '0'*64:
                print 'coinbase!'
                continue
            tx = getTransaction(txid)
            nextInputs += getInputs(tx)
            outputs += getOutputs(tx,outindex)
        inputs = nextInputs
        print len(outputs)
        pprint(inputs)
