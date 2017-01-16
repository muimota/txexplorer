
https://blockexplorer.com/api/rawtx/5756ff16e2b9f881cd15b8a7e478b4899965f87f553b6210d0f8e5bf5be7df1d
http://btc.blockr.io/api/v1/tx/raw/5756ff16e2b9f881cd15b8a7e478b4899965f87f553b6210d0f8e5bf5be7df1d
https://blockchain.info/rawtx/5756ff16e2b9f881cd15b8a7e478b4899965f87f553b6210d0f8e5bf5be7df1d?format=hex
https://insight.bitpay.com/api/rawtx/5756ff16e2b9f881cd15b8a7e478b4899965f87f553b6210d0f8e5bf5be7df1d
https://bitaps.com/api/raw/transaction/5756ff16e2b9f881cd15b8a7e478b4899965f87f553b6210d0f8e5bf5be7df1d
#te lo da en raw, sin cabeceras para el navegador
http://api.qbit.ninja/transactions/5756ff16e2b9f881cd15b8a7e478b4899965f87f553b6210d0f8e5bf5be7df1d?format=raw

*Super big transaction*
9873d0244d71b3358a04675e033d3405e48bfcfe7b65166c34f2942b1ca0e41f

*List of bitcoin explorers*
https://en.bitcoin.it/wiki/Category:Block_chain_browsers

*tests with pybitcointools*
r = requests.get('https://blockchain.info/rawtx/1aa27a456c2f5c019ceb84d3be4b09ed89f800682ebf6fe37794be590164f8fb?format=hex')
txhex = r.text
#txid
txhash(txhex.decode('hex'))
#parse tx
tx = deserialize(txhex.decode('hex'))
#inputs
len(tx['ins'])
#get an input
input = tx['ins'][0]
#input's outpoint txid
input['outpoint']['hash'].encode('hex')
