#! /usr/bin/python3
import bitcoin.rpc
from bitcoin.core import *
from bitcoin.core.script import *
from bitcoin.wallet import *
from bitcoin.core.key import CECKey
import hashlib

PORT = 18444
bitcoin.SelectParams('regtest')
proxy = bitcoin.rpc.Proxy()

h = hashlib.sha256(b'correct horse battery staple').digest()
seckey = CBitcoinSecret.from_secret_bytes(h)
redeemScript = CScript([seckey.pub, OP_CHECKSIG])
      #输入输出都是bytes
script_pub_key = redeemScript.to_p2sh_scriptPubKey()            
p2sh_address = CBitcoinAddress.from_scriptPubKey(script_pub_key)  
# funding_txid = proxy.call("sendtoaddress", str(p2sh_address), 10)
# print(funding_txid)

refunding_address = "2NCdsuJv5F859kWdDf7Wg55CCRjJsG6AFvt"
funding_txid = "5245b199d421bd54e4482348cd37ed48c64665d6ad8bf80a733f5ddc7e4e341e"
vout = 0
txid = lx(funding_txid)
txin = CMutableTxIn(COutPoint(txid,vout))
out_script_pubkey = CBitcoinAddress(refunding_address).to_scriptPubKey()
txout = CMutableTxOut(9.999*COIN, out_script_pubkey)
tx = CMutableTransaction([txin], [txout])   
sighash = SignatureHash(redeemScript, tx, 0 ,SIGHASH_ALL)
sig = seckey.sign(sighash) + bytes([SIGHASH_ALL])
txin.scriptSig = CScript([sig, redeemScript])
spend_txid = proxy.call("sendrawtransaction", b2x(tx.serialize()))
print(spend_txid)
