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
import zmq

PORT = 18444
bitcoin.SelectParams('regtest') 
# proxy = bitcoin.rpc.Proxy()

abspath = os.path.abspath(".") 
base = os.path.basename(abspath) 
LOCKTIME = 2
AMOUNT = 0.001
FEE = 0.00006
MINE_FEE = 0.00003

AMOUNT_FUND = AMOUNT + FEE + MINE_FEE
REFUND_AMOUNT = AMOUNT + 0.00008
REFUND_ADDRESS = '2MtfXC163fwM68WsFkwzPqJQfejiNRHfCbB'

# def get_btc_address():
#     '''return new btc address and save secret used to generate address'''
#     # Generate & Save random address and secret
#     para = base + '_' + str(randint(100000, 9999999999))
#     h = hashlib.sha256(para.encode()).digest()
#     # key = CBitcoinSecret.from_secret_bytes(h)
#     key = CECKey()
#     key.set_secretbytes(h)
#     pubkey = key.get_pubkey()
#     # address = P2PKHBitcoinAddress.from_pubkey(key.get_pubkey())

#     return key, para

def generate_P2SH_address():
    key,para=get_btc_address()
    pubkey=key.get_pubkey()   
    redeemScript= CScript([OP_DUP, OP_HASH160, Hash160(pubkey), OP_EQUALVERIFY, OP_CHECKSIG])
    script_pub_key = redeemScript.to_p2sh_scriptPubKey()
    p2sh_address = CBitcoinAddress.from_scriptPubKey(script_pub_key)
    address_info={"pubkey":pubkey,"redeemScript":redeemScript,"scriptPubKey":script_pub_key,"P2SH_address":p2sh_address}

        # Save generated secret key
    privatekey = {str(p2sh_address): para}
    try:   
        #可换成.pem后缀 
        with open('./keys/privatekey.json','r') as file:
            info=json.load(file)
    except (json.JSONDecodeError,FileNotFoundError) as err:
        with open('./keys/privatekey.json','w') as file:
            json.dump(privatekey,file)
    if 'info' in locals().keys():
        with open('./keys/privatekey.json','w') as file:
            new_info=dict(info,**privatekey)
            json.dump(new_info,file)

    return address_info

def get_key_from_address(address):
    #获取私钥
    try:   
        #可换成.pem后缀 
        with open('./keys/privatekey.json','r') as file:
            info=json.load(file)
    except FileNotFoundError as err: 
        print("cannot find such file") 
        return False
    if address in info.keys():
        para=info[address]
        h = hashlib.sha256(para.encode()).digest()
        # key = CBitcoinSecret.from_secret_bytes(h)
        key = CECKey()
        key.set_secretbytes(h)
        
        return key
    else:
        print("do not exist such key")
        return False

class Sender():
    def __init__(self):    
        self.proxy = bitcoin.rpc.Proxy()
        para = base + '_' + str(randint(100000, 9999999999))
        h = hashlib.sha256(para.encode()).digest()
        self.privkey = CBitcoinSecret.from_secret_bytes(h)
        self.pubkey =  self.privkey.pub       
        self.T_max = 4
        self.locktime = LOCKTIME + self.proxy.call("getblockcount")
        
        self.a = base + '_' + str(randint(100000, 9999999999))
        #commit a
        self.h_1 = hashlib.sha256(self.a.encode()).digest()
        # self.h_1 = Hash160(self.a.encode()) #输出结果是byte
        # commit b
        self.b = base + '?' +str(randint(100000,99999999999))
        # self.h_2 = Hash160((self.b+self.a).encode()) #输出结果是byte
        self.h_2 = hashlib.sha256((self.a+self.b).encode()).digest()
        self.g = hashlib.sha1(self.a.encode()).digest() #输出结果是byte
        #create raw transaction
        self.refunding_address = REFUND_ADDRESS
        self.refund_flag = False
        self.context_mixer = zmq.Context()
        self.socket_mixer = self.context_mixer.socket(zmq.REQ)
        self.socket_mixer.connect("tcp://127.0.0.1:5557")  #连到mixer

    def set_locktime(self,time):
        self.locktime = time
    def set_amount(self,amount):
        self.amount = amount





