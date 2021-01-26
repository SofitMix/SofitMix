#! /usr/bin/python3
import hashlib
import os
from random import randint

import bitcoin.rpc
from bitcoin.core import *
from bitcoin.core.script import *
from bitcoin.wallet import *
from bitcoin.core.key import CECKey
import json

PORT = 18333
bitcoin.SelectParams('testnet') 
# proxy = bitcoin.rpc.Proxy()

abspath = os.path.abspath(".") 
base = os.path.basename(abspath) 

proxy = bitcoin.rpc.Proxy()
para = 'zeromix4'
h = hashlib.sha256(para.encode()).digest()
privkey = CBitcoinSecret.from_secret_bytes(h)
pubkey =  privkey.pub 

para = 'zeromix5'
h = hashlib.sha256(para.encode()).digest()
receiver_privkey = CBitcoinSecret.from_secret_bytes(h)
receiver_pubkey =  privkey.pub 

a = 'zeromixer'
locktime = 4 + proxy.call("getblockcount")
h_1 = hashlib.sha256(a.encode()).digest()

redeemScript = CScript([OP_IF,  OP_SHA256, h_1, OP_EQUALVERIFY, pubkey, OP_CHECKSIG, 
							OP_ELSE, locktime, OP_CHECKLOCKTIMEVERIFY, OP_DROP,
							receiver_pubkey, OP_CHECKSIG, OP_ENDIF])       #输入输出都是bytes
script_pub_key = redeemScript.to_p2sh_scriptPubKey()            #bytes
p2sh_address = CBitcoinAddress.from_scriptPubKey(script_pub_key)  #string
# funding_txid = proxy.call("sendtoaddress", str(p2sh_address), 0.00002)
# print("P2SH_address is:",str(p2sh_address))
# print("txid is:",funding_txid)
# P2SH_address is: 2MvWpiUJ6y7AqeVdB7MR3Smkdib6nrwrzx8
# txid is: 9da786ced718796d1cef05ff012da7e241b7fa1dd62d7ef8cb1a83e5f78070d9

# P2SH_address is: 2MsRtc2eGFDAnzcUV4ZNfZFCqL4Sg7Ej3ez
# txid is: a8fe64d5e19d29361f4f1b6294df8614651e1f87848633244b52722a435af088

# P2SH_address is: 2N3WgvrBdKfFApyETyAiQEEuWDGrYL2PQfU
# txid is: b02560f15d5dee2f3e252dbb4b1160b1164cafab28cdb4a9201d81ba0cad5e71

# P2SH_address is: 2N3WgvrBdKfFApyETyAiQEEuWDGrYL2PQfU
# txid is: 5e2a717dcda82626e2438e470cde63ba0874529212941e43dfd586f5ccbaddf3

funding_txid = "9da786ced718796d1cef05ff012da7e241b7fa1dd62d7ef8cb1a83e5f78070d9"
refunding_address = "2MxP9Yk4CNoZiP3NGTz1Bgu37tnRVtWX2LP"
hextx = proxy.call("gettransaction",funding_txid)['hex']
raw_txid = x(hextx)
temp_tx = CTransaction.deserialize(raw_txid)
tx = CMutableTransaction.from_tx(temp_tx)
if tx.vout[0].scriptPubKey == script_pub_key:
	vout = 0
else:
	vout =1 
txid = lx(funding_txid)
txin = CMutableTxIn(COutPoint(txid,vout))
out_script_pubkey = CBitcoinAddress(str(refunding_address)).to_scriptPubKey()
txout = CMutableTxOut(0.00001*COIN, out_script_pubkey)
tx = CMutableTransaction([txin], [txout])   
sighash = SignatureHash(redeemScript, tx, 0 ,SIGHASH_ALL)
sig = privkey.sign(sighash) + bytes([SIGHASH_ALL])
txin.scriptSig = CScript([sig, a.encode(), OP_TRUE, redeemScript])
spend_txid = proxy.call("sendrawtransaction", b2x(tx.serialize()))
print("P2SH_address is:",str(refunding_address))
print("txid is:",spend_txid)
# P2SH_address is: 2MxP9Yk4CNoZiP3NGTz1Bgu37tnRVtWX2LP
# txid is: 059bb797aa2d212c20c2c52b6479cb8929b5bbec85bd6fac8afcde6944cff100


