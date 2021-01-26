#! /usr/bin/python3
from mixer import *
import time



def exchange_pubkey(proxy,socket,msg):
	global exchange_key, access_exchangekey_time, lock_exkey
	e=2
	if len(msg) != e:
		socket.send(error(len(msg), e))
		return
	pubkey = get_btc_key()
	socket.send(pubkey)

	lock_exkey.acquire()
	exchange_key[b2x(msg[1])] =b2x(pubkey) #sender pubkey:mixer pubkey
	if access_exchangekey_time==0:
		access_exchangekey_time+= 1
		try:	
			with open('./Mixer/keys/exchange_key.json','r') as file:
				prev_key=json.load(file)
		except (json.JSONDecodeError,FileNotFoundError) as err:
			with open('./Mixer/keys/exchange_key.json','w') as file:
				json.dump(exchange_key,file)
		if 'prev_key' in locals().keys():
			with open('./Mixer/keys/exchange_key.json','w') as file:
				exchange_key = dict(prev_key,**exchange_key)
				json.dump(exchange_key,file)
	else:
		with open('./Mixer/keys/exchange_key.json','w') as file:
			json.dump(exchange_key,file)
	lock_exkey.release()
	

	# key_info=[]
	# h = hashlib.sha256(b'correct horse battery staple').digest()
	# seckey1 = CBitcoinSecret.from_secret_bytes(h)
	# str_seckey=b2x(seckey1)
	# x_seckey=x(str_seckey).rstrip(chr(1).encode())

def receive_message(proxy,socket,msg):
	#主要是接受h_1和fund_tx的信息，以便赎回
	#msg = [txid,block_count,sender.pubkey,sender.h_1,sender.locktime]
	global lock_tx,lock_h1, lock_exkey
	e=6
	if len(msg) != e:
		socket.send(error(len(msg), e))
		return 
	
	if int(msg[5])>T_max + proxy.call("getblockcount"):
		socket.send(b"error time")
		return
	blockcount = int(msg[2])
	blockhash = proxy.call("getblockhash",blockcount)
	try:
		#tx on chain
		rawtx = proxy.call("getrawtransaction",msg[1].decode(),True,blockhash)
	except bitcoin.rpc.InvalidAddressOrKeyError as e:
		socket.send(b"cannot get tx")
		return 
	#读取相应的server_pubkey
	lock_exkey.acquire()
	with open('./Mixer/keys/exchange_key.json','r') as file:
		key = json.load(file)
	lock_exkey.release()	
	sender_pubkey = b2x(msg[3])
	try:
		mixer_pubkey = x(key[sender_pubkey])
	except KeyError as e:
		socket.send(b"incorrect pubkey")
		return
	redeem_script = CScript([OP_IF,  OP_SHA256, msg[4], OP_EQUALVERIFY, msg[3], OP_CHECKSIG, 
							OP_ELSE, int(msg[5]), OP_CHECKLOCKTIMEVERIFY, OP_DROP,
							mixer_pubkey, OP_CHECKSIG, OP_ENDIF])

	script_pub_key = redeem_script.to_p2sh_scriptPubKey()
	#can redeem by the mixer
 
	
	try:
		assert rawtx['vout'][0]['scriptPubKey']['hex']==b2x(script_pub_key) or rawtx['vout'][1]['scriptPubKey']['hex']==b2x(script_pub_key)
		locktime = msg[5].decode()

		#locktime:[txid,server_pubkey,redeem_script]
		info = [msg[1].decode(),b2x(mixer_pubkey),b2x(redeem_script)]

		lock_tx.acquire()
		try:	
			with open('./Mixer/file/tx_info.json','r') as file:
				tx_info=json.load(file)
		except (json.JSONDecodeError,FileNotFoundError) as err:
			with open('./Mixer/file/tx_info.json','w') as file:
				tx_info={}
				tx_info[locktime]=[info]
				json.dump(tx_info,file)
		else:
			if locktime in tx_info.keys():
				tx_info[locktime].append(info)
			else:
				tx_info[locktime]=[]
				tx_info[locktime].append(info)
			with open('./Mixer/file/tx_info.json','w') as file:				
				json.dump(tx_info,file)
		lock_tx.release()

		# with open('tx_info.json','r') as file:
		# 	tx_info=json.load(file)
		# 	print(tx_info[locktime])
		#存h_1	
		#locktime:h_1,生成MTree用
		lock_h1.acquire()
		try:
			with open('./Mixer/file/h_1.json','r') as file:
				h1_info = json.load(file)
		except (json.JSONDecodeError, FileNotFoundError) as err:
			with open('./Mixer/file/h_1.json','w') as file:
				h1_info = {}
				h1_info[locktime]=[]
				h1_info[locktime].append(b2x(msg[4]))
				json.dump(h1_info,file)
		else:
			if locktime in h1_info.keys():
				h1_info[locktime].append(b2x(msg[4]))
			else:
				h1_info[locktime]=[]
				h1_info[locktime].append(b2x(msg[4]))
			with open('./Mixer/file/h_1.json','w') as file:
				json.dump(h1_info,file)
		lock_h1.release()
		socket.send(b"correct_tx")
		

	except AssertionError as e:
		socket.send(b"incorrect tx")
		return 

def generate_MTree(proxy,socket,msg):
	global lock_h1
	# print("entering generate_MTree")
	e=1
	if len(msg) != e:
		socket.send(error(len(msg), e))
		return 
	lock_h1.acquire()
	try:
		with open('./Mixer/file/h_1.json','r') as file:
			h1_info = json.load(file)
	except (json.JSONDecodeError, FileNotFoundError) as err:
		socket.send("h_1 file broken, connot generate MTree")
		return
	lock_h1.release()
	hashlist = []
	for list_item in h1_info.values():
		for item in list_item:
			hashlist.append(x(item))

	mt = MerkleTools()
	mt.add_leaf(hashlist)
	mt.make_tree()
	root = mt.get_merkle_root()
	hashlist.insert(0,root)
	
	# print(root.hex())
	socket.send_multipart(hashlist)
	# print("existing generate_MTree")


def redeemtx():
	global lock_h1,lock_tx, lock_refund, lock_key
	print("Entering -> redeemtx")
	proxy = bitcoin.rpc.Proxy()
	needredeem_blockcount = proxy.call("getblockcount")
	while True:
		current_block = proxy.call("getblockcount")
		if needredeem_blockcount<current_block:
			needredeem_blockcount = current_block
		# print(current_block)
		# print(needredeem_blockcount)
		# time.sleep(2)
		if needredeem_blockcount == current_block:
			try:	
				lock_tx.acquire()
				with open('./Mixer/file/tx_info.json','r') as file:
					block_info=json.load(file)
					lock_tx.release()
					str_current_block = str(current_block)
					if str_current_block in block_info.keys():
						print("redeem entering here")
						tx_info = block_info[str_current_block]
						for info in tx_info:
							#[txid,server_pubkey,redeem_script]
							#读取mixer的私钥
							try:   
								lock_refund.acquire()
								with open('./Mixer/file/refunded_tx.json','r') as file:
									pre_tx=json.load(file)
									lock_refund.release()
									# print(pre_tx)
									print("当前检验的是:",info[0])
									if info[0] in pre_tx:
										print("此交易已被赎回：",info[0])
										continue
							except (json.JSONDecodeError,FileNotFoundError) as e:
								lock_refund.release()
								continue


							try:
								lock_key.acquire()
								with open('./Mixer/keys/mixer_key.json','r') as file:
									key=json.load(file)
									lock_key.release()
									print("use pubkey:",info[1])
									if info[1] in key.keys():
										tem_privkey = key[info[1]]
										mixer_privkey = CBitcoinSecret.from_secret_bytes(x(tem_privkey))
									else:
										print("cannot redeem this tx, lose privatekey")
										# print("Exiting -> redeemtx")
										continue
							except (json.JSONDecodeError,FileNotFoundError) as err1:
								lock_key.release()
								print("cannot redeem this tx, lose privkey file")
								# print("Exiting -> redeemtx")
								continue
								
							redeem_script = CScript(x(info[2]))
							script_pub_key = redeem_script.to_p2sh_scriptPubKey()
							#自动定位utxo
							hextx = proxy.call("gettransaction",info[0])['hex']
							raw_txid = x(hextx)
							temp_tx = CTransaction.deserialize(raw_txid)
							tx = CMutableTransaction.from_tx(temp_tx)
							if tx.vout[0].scriptPubKey == script_pub_key:
								vout = 0
							else:
								vout =1 
							txid = lx(info[0])
							txin = CMutableTxIn(COutPoint(txid,vout), nSequence = 0)
							mixer_address = proxy.call("getnewaddress")
							out_script_pubkey = CBitcoinAddress(str(mixer_address)).to_scriptPubKey()
							txout = CMutableTxOut(REDEEM_AMOUNT*COIN, out_script_pubkey)
							tx = CMutableTransaction([txin], [txout], nLockTime = current_block)   
							sighash = SignatureHash(redeem_script, tx, 0 ,SIGHASH_ALL)
							sig = mixer_privkey.sign(sighash) + bytes([SIGHASH_ALL])
							txin.scriptSig = CScript([sig, OP_FALSE, redeem_script])
							while True:
								try:
									spend_txid = sender.proxy.call("sendrawtransaction", b2x(tx.serialize()))
									break
								except VerifyError as e:
									time.sleep(3)

							print("redeeming tx",spend_txid)
						#删除已赎回的交易
						lock_tx.acquire()
						with open('./Mixer/file/tx_info.json','r') as file1:
							block_info=json.load(file1)
							del block_info[str_current_block]
						with open('./Mixer/file/tx_info.json','w') as file1:
							json.dump(block_info,file1)
						lock_tx.release()
						#删除已过期的h_1	
						lock_h1.acquire()
						with open('./Mixer/file/h_1.json','r') as file2:
							h_1_info=json.load(file2)
							del h_1_info[str_current_block]
						with open('./Mixer/file/h_1.json','w') as file2:
							json.dump(h_1_info,file2)
						lock_h1.release()

					needredeem_blockcount += 1
			except (json.JSONDecodeError,FileNotFoundError) as err2:
				lock_refund.release()
				needredeem_blockcount += 1


def refund_tx(proxy,socket,msg):
	#can use api https://www.blockcypher.com/dev/bitcoin/#introduction to construct scrapy in practice. 
	global lock_refund,lock_listg, lock_mixer_redeemscript, lock_key, lock_code
	e=3
	if len(msg) != e:
		socket.send(error(len(msg), e))
		return 
	#[b"refund_tx",sender.a.encode(),funding_txid.encode()]
	socket.send(b"I know")

	lock_refund.acquire()
	list_tx = [msg[2].decode()]
	try:   
		with open('./Mixer/file/refunded_tx.json','r') as file:
			pre_tx=json.load(file)
	except (json.JSONDecodeError,FileNotFoundError) as err:
		with open('./Mixer/file/refunded_tx.json','w') as file:
			json.dump(list_tx,file)
	if 'pre_tx' in locals().keys():
		with open('./Mixer/file/refunded_tx.json','w') as file:
			list_tx += pre_tx
			json.dump(list_tx,file)
	lock_refund.release()

	g = hashlib.sha1(msg[1]).digest().hex()

	lock_listg.acquire()
	# print('I got lock_listg---%s'%(time.ctime()))

	list_g = [g]
	try:   
		with open('./Mixer/file/list_g.json','r') as file:
			pre_g=json.load(file)
	except (json.JSONDecodeError,FileNotFoundError) as err:
		with open('./Mixer/file/list_g.json','w') as file:
			json.dump(list_g,file)
	if 'pre_g' in locals().keys():
		with open('./Mixer/file/list_g.json','w') as file:
			list_g += pre_g
			json.dump(list_g,file)

	# print('I release lock_listg---%s'%(time.ctime()))
	lock_listg.release()
	

	try:
		lock_code.acquire()		
		lock_mixer_redeemscript.acquire()
		# print('I got lock_mixer_redeemscript---%s'%(time.ctime()))
		
		# print('I got lock_code---%s'%(time.ctime()))
		with open('./Mixer/file/mixer_redeemscript_info.json','r') as file:
			mixer_redeemscript_info=json.load(file)
			lock_mixer_redeemscript.release()
			
			# print(g)
			
			if g in mixer_redeemscript_info.keys(): #说明mixer已经生成了对应g的tx，这时需要赎回。
				#g:[funding_txid, b.decode(), h2.hex(), receiver_pubkey.hex(), mixer_pubkey.hex(),locktime]
				lock_code.release()
				# print('I release lock_code at 1---%s'%(time.ctime()))
				redeemscript_info = mixer_redeemscript_info[g]
				try:
					lock_key.acquire()
					with open('./Mixer/keys/mixer_key.json','r') as file:
						key=json.load(file)
						lock_key.release()
						# print('I release lock_key at 1---%s'%(time.ctime()))
						# print("use pubkey:",info[1])
						if redeemscript_info[4] in key.keys():
							tem_privkey = key[redeemscript_info[4]]
							mixer_privkey = CBitcoinSecret.from_secret_bytes(x(tem_privkey))
						else:
							print("cannot get refund, lose privatekey")
				except (json.JSONDecodeError,FileNotFoundError) as err1:
					lock_key.release()
					# print('I release lock_key at 2---%s'%(time.ctime()))
					print("cannot refund, lose privkey file")

				if 'mixer_privkey' in locals().keys():

					redeem_script =  CScript([OP_IF,  OP_SHA256, x(redeemscript_info[2]), OP_EQUALVERIFY, x(redeemscript_info[4]), OP_CHECKSIG, 
											OP_ELSE, redeemscript_info[5], OP_CHECKLOCKTIMEVERIFY, OP_DROP,
											x(redeemscript_info[3]), OP_CHECKSIG, OP_ENDIF])
					script_pub_key = redeem_script.to_p2sh_scriptPubKey()
					#自动定位utxo
					hextx = proxy.call("gettransaction",redeemscript_info[0])['hex']
					raw_txid = x(hextx)
					temp_tx = CTransaction.deserialize(raw_txid)
					tx = CMutableTransaction.from_tx(temp_tx)
					if tx.vout[0].scriptPubKey == script_pub_key:
						vout = 0
					else:
						vout =1 
					txid = lx(redeemscript_info[0])
					txin = CMutableTxIn(COutPoint(txid,vout))
					out_script_pubkey = CBitcoinAddress(REFUND_ADDRESS).to_scriptPubKey()
					txout = CMutableTxOut(REFUND_AMOUNT*COIN, out_script_pubkey)
					tx = CMutableTransaction([txin], [txout])   
					sighash = SignatureHash(redeem_script, tx, 0 ,SIGHASH_ALL)
					sig = mixer_privkey.sign(sighash) + bytes([SIGHASH_ALL])
					txin.scriptSig = CScript([sig, (msg[1].decode()+redeemscript_info[1]).encode(), OP_TRUE, redeem_script])
					# print(b2x(tx.serialize()))
					# print("h_2 is:",b2x(hashlib.sha256((msg[1].decode()+redeemscript_info[1]).encode()).digest()))
					while True:
						try:
							spend_txid = sender.proxy.call("sendrawtransaction", b2x(tx.serialize()))
							break
						except VerifyError as e:
							time.sleep(3)

					print("refund_tx",spend_txid)

					context_receiver = zmq.Context()
					socket_receiver = context_receiver.socket(zmq.REQ)
					socket_receiver.connect("tcp://127.0.0.1:5558") 
					refund_info = [b"refunded_tx",redeemscript_info[0].encode()]			
					socket_receiver.send_multipart(refund_info)
					socket_receiver.recv()
					socket_receiver.close()
					context_receiver.term()
			else:
				
				lock_code.release()
				# print('I release lock_key at 3---%s'%(time.ctime()))
				print("g is not in mixer_redeemscript_info, the tx has not generated yet")

	except (json.JSONDecodeError,FileNotFoundError) as err:
		lock_code.release()
		# print('I release lock_code at 2---%s'%(time.ctime()))
		lock_mixer_redeemscript.release()
		
	
		
		




options = {
	"exchange_pubkey": exchange_pubkey,
	"send_message_to_mixer":receive_message,
	"request_for_MTree":generate_MTree,
	"refund_tx":refund_tx
}

function_name = {
	"exchange_pubkey": 'exchange_pubkey',
	"send_message_to_mixer":'receive_message',
	"request_for_MTree":'generate_MTree',
	"refund_tx":"refund_tx"
}



def worker_routine(worker_url, context=None):
	"""Worker routine"""
	context = context or zmq.Context.instance()
	# Socket to talk to dispatcher
	socket = context.socket(zmq.REP)
	socket.connect(worker_url)
	# exchange_key = {}
	try:
		proxy = bitcoin.rpc.Proxy()
		while True:
			msg = socket.recv_multipart()
			# print "Received message %s" % msg
			if msg[0].decode() in options.keys():
				print("Entering -> %s" % function_name[msg[0].decode()])
				options[msg[0].decode()](proxy,socket, msg)
				print("Exiting -> %s" % function_name[msg[0].decode()])

			else:
				# printf
				socket.send(b"METHOD NOT AVAILABLE")
	except KeyboardInterrupt:
		print("Interrupt received. Stoping ....")


def main1():
	print(' mixer_server %s is runing' % os.getpid())
	"""Server routine"""
	t = threading.Thread(target = redeemtx)
	t.start()

	url_worker = "inproc://worker"
	url_client = "tcp://127.0.0.1:5557"
	# Prepare our context and sockets
	context = zmq.Context.instance()
	# Socket to talk to clients
	clients = context.socket(zmq.ROUTER)
	clients.bind(url_client)
	# Socket to talk to workers
	workers = context.socket(zmq.DEALER)
	workers.bind(url_worker)
	# Launch pool of worker threads
	for i in range(400):
		thread = threading.Thread(target=worker_routine, args=(url_worker,))
		thread.start()
	zmq.proxy(clients, workers)
	# We never get here but clean up anyhow
	clients.close()
	workers.close()
	context.term()

# if __name__ == "__main__":
# 	main()