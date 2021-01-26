#! /usr/bin/python3
import zmq
import bitcoin.rpc
from bitcoin.core import *
from bitcoin.core.script import *
from bitcoin.wallet import *
from bitcoin.core.key import CECKey
import hashlib

PORT = 18333
bitcoin.SelectParams('regtest') 
proxy = bitcoin.rpc.Proxy()
TIMELOCK = 2
timelock = proxy.call("getblockcount") + TIMELOCK
# para = 'zeromix_5619830903'
# h = hashlib.sha256(para.encode()).digest()
# seckey = CBitcoinSecret.from_secret_bytes(h)
# pubkey = seckey.pub
para1 = 'zeromix_5619830903'
para2 = 'zeromix_5619830904'
h1 = hashlib.sha256(para1.encode()).digest()
h2 = hashlib.sha256(para2.encode()).digest()
seckey1 = CBitcoinSecret.from_secret_bytes(h1)
seckey2 = CBitcoinSecret.from_secret_bytes(h2)
sender_pubkey = seckey1.pub
receiver_pubkey = seckey2.pub

#test script in zeromixer:
a = 'zeromix_5619830902'
h_1 = Hash160(a.encode())
#create raw transaction

locktime = 121                   
redeemScript = CScript([OP_IF,  OP_HASH160, h_1, OP_EQUALVERIFY, sender_pubkey, OP_CHECKSIG, 
					OP_ELSE, locktime, OP_CHECKLOCKTIMEVERIFY, OP_DROP,
					receiver_pubkey, OP_CHECKSIG, OP_ENDIF])       #输入输出都是bytes
script_pub_key = redeemScript.to_p2sh_scriptPubKey()            #bytes
p2sh_address = CBitcoinAddress.from_scriptPubKey(script_pub_key)  #string
funding_txid = proxy.call("sendtoaddress", str(p2sh_address), 5)
print(funding_txid)

#refunding tx:
# newaddress = proxy.getnewaddress()
# print(newaddress)
# funding_txid = 'ffdef1a36d93c3bc0da7f6c11757e526082f4f468ee7046436935245cba9b4db'
# redeem_script = redeemScript
# script_pub_key = redeem_script.to_p2sh_scriptPubKey()
# #自动定位utxo
# hextx = proxy.call("gettransaction",funding_txid)['hex']
# raw_txid = x(hextx)
# temp_tx = CTransaction.deserialize(raw_txid)
# tx = CMutableTransaction.from_tx(temp_tx)
# print(b2x(tx.vout[0].scriptPubKey))
# print(script_pub_key)
# if tx.vout[0].scriptPubKey == script_pub_key:
# 	vout = 0
# else:
# 	vout =1 
# txid = lx(funding_txid)
# txin = CMutableTxIn(COutPoint(txid,vout))
# out_script_pubkey = CBitcoinAddress(str(newaddress)).to_scriptPubKey()
# txout = CMutableTxOut(4.999*COIN, out_script_pubkey)
# # print("now:",proxy.call("getblockcount"))
# tx = CMutableTransaction([txin], [txout])   
# sighash = SignatureHash(redeem_script, tx, 0 ,SIGHASH_ALL)
# sig = seckey1.sign(sighash) + bytes([SIGHASH_ALL])
# txin.scriptSig = CScript([sig, a.encode(), OP_TRUE, redeem_script])
# spend_txid = proxy.call("sendrawtransaction", b2x(tx.serialize()))
# print(spend_txid)
# print(len(tx.serialize()))


#spending tx:
funding_txid = "01c9a808274711adb17e5a18654938be8cb013f5fe12a00d8dc06a4b56cf28fa"
redeem_script = redeemScript
script_pub_key = redeem_script.to_p2sh_scriptPubKey()
newaddress = proxy.call("getnewaddress")
#自动定位utxo
hextx = proxy.call("gettransaction",funding_txid)['hex']
raw_txid = x(hextx)
temp_tx = CTransaction.deserialize(raw_txid)
tx = CMutableTransaction.from_tx(temp_tx)
if tx.vout[0].scriptPubKey == script_pub_key:
	vout = 0
else:
	vout =1 
txid = lx(funding_txid)

txin = CMutableTxIn(COutPoint(txid,vout),nSequence = 0)
out_script_pubkey = CBitcoinAddress(newaddress).to_scriptPubKey()
txout = CMutableTxOut(4.999*COIN, out_script_pubkey)
print("now:",proxy.call("getblockcount"))
tx = CMutableTransaction([txin], [txout], nLockTime = 121)
sighash = SignatureHash(redeem_script, tx, 0 ,SIGHASH_ALL)
sig = seckey2.sign(sighash) + bytes([SIGHASH_ALL])
txin.scriptSig = CScript([sig, OP_FALSE ,redeem_script])
spend_txid = proxy.call("sendrawtransaction", b2x(tx.serialize()))
print(spend_txid)


#test Ntimelock

#setup_funding_TX
# redeem_script = CScript([timelock, OP_CHECKLOCKTIMEVERIFY, OP_DROP, pubkey, OP_CHECKSIG])
# script_pub_key = redeem_script.to_p2sh_scriptPubKey()
# p2sh_address = CBitcoinAddress.from_scriptPubKey(script_pub_key)
# funding_txid = proxy.call("sendtoaddress",str(p2sh_address),1)
# print(funding_txid)

#spend_funding_TX
# funding_txid = "fceb24e162c58f30b900a3517f010148be1c65d07ffda009399705a19a187624"
# redeem_script = CScript([118, OP_CHECKLOCKTIMEVERIFY, OP_DROP, pubkey, OP_CHECKSIG])
# script_pub_key = redeem_script.to_p2sh_scriptPubKey()
# newaddress = proxy.call("getnewaddress")
# #自动定位utxo
# hextx = proxy.call("gettransaction",funding_txid)['hex']
# raw_txid = x(hextx)
# temp_tx = CTransaction.deserialize(raw_txid)
# tx = CMutableTransaction.from_tx(temp_tx)
# if tx.vout[0].scriptPubKey == script_pub_key:
# 	vout = 0
# else:
# 	vout =1 
# txid = lx(funding_txid)

# txin = CMutableTxIn(COutPoint(txid,vout),nSequence = 0)
# out_script_pubkey = CBitcoinAddress(newaddress).to_scriptPubKey()
# txout = CMutableTxOut(0.999*COIN, out_script_pubkey)
# print("now:",proxy.call("getblockcount"))
# tx = CMutableTransaction([txin], [txout], nLockTime = proxy.call("getblockcount"))
# sighash = SignatureHash(redeem_script, tx, 0 ,SIGHASH_ALL)
# sig = seckey.sign(sighash) + bytes([SIGHASH_ALL])
# txin.scriptSig = CScript([sig, redeem_script])
# spend_txid = proxy.call("sendrawtransaction", b2x(tx.serialize()))
# print(spend_txid)


#test normal TX: right

#setup_funding_TX
# redeem_script = CScript([ pubkey, OP_CHECKSIG])
# script_pub_key = redeem_script.to_p2sh_scriptPubKey()
# print(script_pub_key) #b'\xa9\x14\xc8,\x1e1R\xb5\x98\xc8\xeb\xba;\xed\x05\x90"\x17\xe4\t\xffN\x87'
# p2sh_address = CBitcoinAddress.from_scriptPubKey(script_pub_key)
# funding_txid = proxy.call("sendtoaddress",str(p2sh_address),1)
# print(funding_txid)

# funding_txid = "ca1a6de61efd65e31707282d1defccffbaa9fb8d0ae0ee006dd04f446a0535eb"
# hextx = proxy.call("gettransaction",funding_txid)['hex']
# raw_txid = x(hextx)
# temp_tx = CTransaction.deserialize(raw_txid)
# tx = CMutableTransaction.from_tx(temp_tx)
# print(tx.vout[0].nValue/COIN) #1 
# print(tx.vout[0].scriptPubKey)  #b'\xa9\x14\xc8,\x1e1R\xb5\x98\xc8\xeb\xba;\xed\x05\x90"\x17\xe4\t\xffN\x87' 与上面一样


#spend_funding_TX
# funding_txid = "ca1a6de61efd65e31707282d1defccffbaa9fb8d0ae0ee006dd04f446a0535eb"
# redeem_script = CScript([ pubkey, OP_CHECKSIG])
# newaddress = proxy.call("getnewaddress")
# txid = lx(funding_txid)
# vout = 0
# txin = CMutableTxIn(COutPoint(txid,vout))
# out_script_pubkey = CBitcoinAddress(newaddress).to_scriptPubKey()
# txout = CMutableTxOut(0.999*COIN, out_script_pubkey)
# tx = CMutableTransaction([txin], [txout])
# sighash = SignatureHash(redeem_script, tx, 0 ,SIGHASH_ALL)
# sig = seckey.sign(sighash) + bytes([SIGHASH_ALL])
# txin.scriptSig = CScript([sig, redeem_script])
# spend_txid = proxy.call("sendrawtransaction", b2x(tx.serialize()))
# print(spend_txid)


#test nTimeLock TX

#setup_funding_TX
# redeem_script = CScript([ pubkey, OP_CHECKSIG])
# script_pub_key = redeem_script.to_p2sh_scriptPubKey()
# p2sh_address = CBitcoinAddress.from_scriptPubKey(script_pub_key)
# funding_txid = proxy.call("sendtoaddress",str(p2sh_address),0.0001)
# print(funding_txid)



# spend_funding_TX
# funding_txid = "6bf718b4fb47f19979c1fd1942f848981826e67807b29c542ce152caa28b551d"
# redeem_script = CScript([ pubkey, OP_CHECKSIG])
# script_pub_key = redeem_script.to_p2sh_scriptPubKey()
# newaddress = proxy.call("getnewaddress")
# txid = lx(funding_txid)
# hextx = proxy.call("gettransaction",funding_txid)['hex']
# raw_txid = x(hextx)
# temp_tx = CTransaction.deserialize(raw_txid)
# tx = CMutableTransaction.from_tx(temp_tx)
# if tx.vout[0].scriptPubKey == script_pub_key:
# 	vout = 0
# else:
# 	vout =1 
# txin = CMutableTxIn(COutPoint(txid,vout),nSequence = 0)
# out_script_pubkey = CBitcoinAddress(newaddress).to_scriptPubKey()
# txout = CMutableTxOut(0.000098*COIN, out_script_pubkey)
# tx = CMutableTransaction([txin], [txout],nLockTime = proxy.getblockcount())
# sighash = SignatureHash(redeem_script, tx, 0 ,SIGHASH_ALL)
# sig = seckey.sign(sighash) + bytes([SIGHASH_ALL])
# txin.scriptSig = CScript([sig, redeem_script])
# spend_txid = proxy.call("sendrawtransaction", b2x(tx.serialize()))
# print(spend_txid)

#test check TX
# redeem_script = CScript([ pubkey, OP_CHECKSIG])
# script_pub_key = redeem_script.to_p2sh_scriptPubKey()
# p2sh_address = CBitcoinAddress.from_scriptPubKey(script_pub_key)
# blockcount = proxy.call("getblockcount")
# funding_txid = proxy.call("sendtoaddress",str(p2sh_address),0.0001)
# print(funding_txid)

# print(blockcount)
	
		
# def check_TX(txid,blockcount):
# 	#check whether this tx is confirmed
# 	current_count = proxy.call("getblockcount")
# 	if blockcount!=current_count:
# 		blockhash = proxy.call("getblockhash",current_count)
# 		try:
# 			rawtx = proxy.call("getrawtransaction",txid,0,blockhash)
# 			return rawtx, current_count
# 		except bitcoin.rpc.InvalidAddressOrKeyError as e:
# 			return 0, current_count
# 	else:
# 		return 0,current_count

# rawtx,blockcount = check_TX(funding_txid,blockcount)
# while (not rawtx):	
# 	rawtx,blockcount = check_TX(funding_txid,blockcount)

# print("end")
# print(proxy.call("getrawtransaction",funding_txid,0,blockhash))