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
import threading

PORT = 18444
bitcoin.SelectParams('regtest')
abspath = os.path.abspath(".") 
base = os.path.basename(abspath) 
REDEEM_AMOUNT = 0.001
lock_key = threading.Lock()
lock_tx = threading.Lock()
lock_refund = threading.Lock()

class Receiver():

	def __init__(self):

		self.proxy = bitcoin.rpc.Proxy()
		para = base + '_' + str(randint(100000, 9999999999))
		h = hashlib.sha256(para.encode()).digest()
		self.privkey = CBitcoinSecret.from_secret_bytes(h)
		self.pubkey =  self.privkey.pub 
		self.T_max = 2






