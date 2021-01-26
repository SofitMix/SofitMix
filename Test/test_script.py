#! /usr/bin/python3

#测试结果：使用CBitcoinSecret方式生成公钥长度33，redeemscript长度163，使用CECKey()方式生成公钥长度65，redeemscript长度99
#Cscript 输入输出都是bytes， to_p2sh_scriptPubKey， from_scriptPubKey输出都是bytes

import logging
import hashlib
import os
from random import randint

import bitcoin.rpc
from bitcoin.core import *
from bitcoin.core.script import *
from bitcoin.wallet import *
from bitcoin.core.key import CECKey
import json
import zmq

PORT = 18333
bitcoin.SelectParams('regtest') 
proxy = bitcoin.rpc.Proxy()
key_info={}  #server公钥：私钥
exchange_key={} #sender公钥:server公钥
T_max=4
LOCKTIME= 6
AMOUNT = 0.001
MINE_FEE = 0.00005

AMOUNT_FUND = AMOUNT + MINE_FEE


def generate_fundingTX():


	para1 = 'zeromix_5619830903'
	para2 = 'zeromix_5619830904'
	h1 = hashlib.sha256(para1.encode()).digest()
	h2 = hashlib.sha256(para2.encode()).digest()
	seckey1 = CBitcoinSecret.from_secret_bytes(h1)
	seckey2 = CBitcoinSecret.from_secret_bytes(h2)
	sender_pubkey = seckey1.pub
	receiver_pubkey = seckey2.pub

	# sender_pubkey = b'\x04\xd5t]\x83p\xces\xaa\x82\xa8\n\x10\x12\x88\xa5Rm\x89\x86\x88}ON\x14\x8b>z-5d:h\xcb\n#z\x1enV\xd7 \x1b\x03[bui\xaa\x12\xd2\xbd\xfbB)T:\x994\x8e\xf5\x1f\x87N\xbf'
	# receiver_pubkey = b"\x046\xbe\\\xc7xL\x00\x07\xbd\xdbM^\xfa\x02\x92\x9f2!\x85Qg\x88\xb5o\xa5'7\xe1\xb19\r\x08q\xd5M\xda\x0f\x08\x8d\xc7\xad_\xc6<\x10\x82\x84\xbe-J\x99\x9d\xac\x89~b\xc6\x12\xac\xa5\x05\xea\xca\x83"

	a = 'zeromix_5619830905'
	h_1 = Hash160(a.encode()) #输出结果是byte b'\xe2{\x1a\x96\x979\xcf2]\xdb\xc1\x07\xc7\xae\x02/ i0\xbd'

	#create raw transaction

	locktime = LOCKTIME
	redeemScript = CScript([OP_IF,  OP_HASH160, h_1, OP_EQUALVERIFY, sender_pubkey, OP_CHECKSIG, 
						OP_ELSE, locktime, OP_CHECKLOCKTIMEVERIFY, OP_DROP,
						receiver_pubkey, OP_CHECKSIG, OP_ENDIF])    
	print(b2x(redeemScript))  
	print(len(redeemScript))
	script_pub_key = redeemScript.to_p2sh_scriptPubKey()
	print(b2x(script_pub_key))
	p2sh_address = CBitcoinAddress.from_scriptPubKey(script_pub_key)
	print(p2sh_address)
    
	address_info=[redeemScript,p2sh_address]
	print(address_info)

	print(b2x(sender_pubkey))
	print(b2x(receiver_pubkey))
	print(b2x(h_1))
	print(len(redeemScript))

	
generate_fundingTX()



