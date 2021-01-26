#! /usr/bin/python3
import zmq
import bitcoin.rpc
from bitcoin.core import *
from bitcoin.core.script import *
from bitcoin.wallet import *
from bitcoin.core.key import CECKey
import json
from mixer_merkletree import *
import os
from random import randint
import hashlib
import threading 
import os

PORT = 18444
bitcoin.SelectParams('regtest') 
# key_info={}  #server公钥：私钥
exchange_key={} #sender公钥:server公钥
T_max=2
LOCKTIME= 2
AMOUNT = REFUND_AMOUNT  = 0.001
REDEEM_AMOUNT = AMOUNT + 0.00008
MINE_FEE = 0.00001
access_getkey_time = 0
access_exchangekey_time = 0
AMOUNT_FUND = AMOUNT + MINE_FEE
REFUND_ADDRESS = "2N4uNkT9d72GFugGmVayRR5zKEfYoH2fXk8"

lock_exkey = threading.Lock()
lock_tx = threading.Lock()
lock_listg = threading.Lock()
lock_refund = threading.Lock()
lock_h1 = threading.Lock()
lock_mixer_redeemscript = threading.Lock()
lock_key = threading.Lock()
lock_code = threading.Lock()
# plock_mixer_redeemscript = multiprocessing.Lock()
# plock_listg = multiprocessing.Lock()
# plock_key = multiprocessing.Lock()

def get_btc_key():
    global lock_key
    # global access_getkey_time, key_info
    '''return new btc address and save secret used to generate address'''
    # Generate & Save random address and secret
    abspath = os.path.abspath(".") 
    base = os.path.basename(abspath)
    para = base + '_' + str(randint(100000, 9999999999))
    h = hashlib.sha256(para.encode()).digest()
    # key = CBitcoinSecret.from_secret_bytes(h)
    privkey = CBitcoinSecret.from_secret_bytes(h)
    pubkey =  privkey.pub 

    # seckey = CBitcoinSecret.from_secret_bytes(h)
    # pubkey = seckey.pub
    key_info = {b2x(pubkey):b2x(privkey)}
    # key_info[b2x(pubkey):] = b2x(privkey)
    # print("store pubkey:", b2x(pubkey))
    # print("store privkey:", b2x(privkey))
    # print("access_getkey_time:",access_getkey_time)
    # if access_getkey_time==0:
    #     access_getkey_time = 1
    lock_key.acquire()
    try:    
        with open('./Mixer/keys/mixer_key.json','r') as file:
            prev_key=json.load(file)
    except (json.JSONDecodeError,FileNotFoundError) as err:
        with open('./Mixer/keys/mixer_key.json','w') as file:
            json.dump(key_info,file)
    if 'prev_key' in locals().keys():
        with open('./Mixer/keys/mixer_key.json','w') as file:
            key_info = dict(prev_key,**key_info)
            json.dump(key_info,file)
    lock_key.release()

    return pubkey
    # pubkey = key.get_pubkey()
    # address = P2PKHBitcoinAddress.from_pubkey(key.get_pubkey())

def error(n, e):
	return b"Wrong number of arguments" + \
       b"got %d expected %d" % (n, e)