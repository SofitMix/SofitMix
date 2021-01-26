#! /usr/bin/python3

from receiver import *
import time

receiver_key = {}
access_getkey_time = 0
old_thread_num = 0

#可能类型不一样
def error(n, e):
	return "Wrong number of arguments" + \
		"got %d expected %d" % (n, e)

def request_for_MTree(socket,msg):
	e=1
	if len(msg) != e:
		socket.send(error(len(msg), e))
		return
	#corresponding txid

	context_mixer = zmq.Context()
	socket_mixer = context_mixer.socket(zmq.REQ)
	socket_mixer.connect("tcp://127.0.0.1:5557")
	send_info = b"request_for_MTree"		
	socket_mixer.send(send_info)
	# reply = [root,hashlist]
	print(4)
	reply = socket_mixer.recv_multipart()
	print(5)
	socket_mixer.close()
	context_mixer.term()
	#to sender

	socket.send_multipart(reply)

def send_zkproof_to_mixer(socket,msg):
	global receiver_key, access_getkey_time, lock_key, lock_tx

	e = 5
	if len(msg) != e:
		socket.send(error(len(msg), e))
		return
	receiver = Receiver()
	#存pubkey：privkey

	lock_key.acquire()
	receiver_key[b2x(receiver.pubkey)] = b2x(receiver.privkey)
	if access_getkey_time==0:
		access_getkey_time = 1
	try:    
		with open('./Receiver/keys/receiver_key.json','r') as file:
			prev_key=json.load(file)
	except (json.JSONDecodeError,FileNotFoundError) as err:
		with open('./Receiver/keys/receiver_key.json','w') as file:
			json.dump(receiver_key,file)
	if 'prev_key' in locals().keys():
		with open('./Receiver/keys/receiver_key.json','w') as file:
			receiver_key = dict(prev_key,**receiver_key)
			json.dump(receiver_key,file)
	else:
		with open('./Receiver/keys/mixer_key.json','w') as file:
			json.dump(receiver_key,file)
	lock_key.release()

	context_mixer = zmq.Context()
	socket_mixer = context_mixer.socket(zmq.REQ)
	socket_mixer.connect("tcp://127.0.0.1:5556")
	msg.insert(4,receiver.pubkey)
	# ["ZKproof",sender.b,sender.g,sender.h_2,receiver.pubkey,pi]
	socket_mixer.send_multipart(msg)
	print(2)
	reply = socket_mixer.recv_multipart() 
	print(3)
	# [ funding_txid, block_count, mixer_pubkey, locktime], h2, receiver_pubkey,从上面获取
	e=4
	if len(reply) != e:
		print(reply[0].decode())
		print("length is not correct")
		socket.send(reply[0]) #to sender "TX already redeemed by sender"
		return 
	blockcount = int(reply[1])
	blockhash = receiver.proxy.call("getblockhash",blockcount)
	try:
		#tx on chain
		rawtx = receiver.proxy.call("getrawtransaction",reply[0].decode(),True,blockhash)
	except bitcoin.rpc.InvalidAddressOrKeyError as e:
		socket.send(b"cannot get tx")
		return 

	redeem_script = CScript([OP_IF,  OP_SHA256, msg[3], OP_EQUALVERIFY, reply[2] , OP_CHECKSIG, 
							OP_ELSE, int(reply[3]), OP_CHECKLOCKTIMEVERIFY, OP_DROP,
							msg[4], OP_CHECKSIG, OP_ENDIF])
	script_pub_key = redeem_script.to_p2sh_scriptPubKey()
	#can redeem by receiver
	try:
		assert rawtx['vout'][0]['scriptPubKey']['hex']==b2x(script_pub_key) or rawtx['vout'][1]['scriptPubKey']['hex']==b2x(script_pub_key)
		locktime = reply[3].decode()
		#locktime:[txid,receiver_pubkey,redeem_script]
		info = [reply[0].decode(),b2x(receiver.pubkey),b2x(redeem_script)]
		#赎回时用pubkey找相应的privkey

		lock_tx.acquire()
		try:	
			with open('./Receiver/file/receiver_tx_info.json','r') as file:
				tx_info=json.load(file)
		except (json.JSONDecodeError,FileNotFoundError) as err:
			with open('./Receiver/file/receiver_tx_info.json','w') as file:
				tx_info={}
				tx_info[locktime]=[info]
				json.dump(tx_info,file)
		else:
			if locktime in tx_info.keys():
				tx_info[locktime].append(info)
			else:
				tx_info[locktime]=[]
				tx_info[locktime].append(info)
			with open('./Receiver/file/receiver_tx_info.json','w') as file:				
				json.dump(tx_info,file)
		lock_tx.release()

		reply.insert(2,msg[3])
		reply.insert(3,receiver.pubkey)
		socket.send_multipart(reply) #发给sender [funding_txid, block_count, h2, receiver_pubkey, mixer_pubkey, LOCKTIME] 

	except AssertionError as e:
		print("incorrect tx")
		socket.send("incorrect tx") 
		return 

def redeemtx():
	global lock_tx,lock_refund,lock_key
	print("Entering -> redeemtx")
	proxy = bitcoin.rpc.Proxy()
	needredeem_blockcount = proxy.call("getblockcount")
	while True:
		current_block = proxy.call("getblockcount")
		# print(current_block)
		# print(needredeem_blockcount)
		# time.sleep(2)
		if needredeem_blockcount == current_block:
			try:
				lock_tx.acquire()	
				with open('./Receiver/file/receiver_tx_info.json','r') as file:
					block_info=json.load(file)
					lock_tx.release()
					str_current_block = str(current_block)
					if str_current_block in block_info.keys():
						# print("entering here")
						tx_info = block_info[str_current_block]
						for info in tx_info:
							#[txid,receiver_pubkey,redeem_script]
							#读取receiver的私钥
							try:  
								lock_refund.acquire() 
								with open('./Receiver/file/refunded_tx.json','r') as file:
									pre_tx=json.load(file)
									lock_refund.release()
									if info[0] in pre_tx:
										continue
							except (json.JSONDecodeError,FileNotFoundError) as e:
								lock_refund.release()
								continue

							try:
								lock_key.acquire()
								with open('./Receiver/keys/receiver_key.json','r') as file:
									key=json.load(file)
									lock_key.release()
									if info[1] in key.keys():
										tem_privkey = key[info[1]]
										receiver_privkey = CBitcoinSecret.from_secret_bytes(x(tem_privkey))
									else:
										print("cannot redeem this tx, lose privkey")
										# print("Exiting -> redeemtx")
										continue
							except (json.JSONDecodeError,FileNotFoundError) as err1:
								lock_key.release()
								print("cannot redeem this tx, lose privkey")
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
							receiver_address = proxy.call("getnewaddress")
							out_script_pubkey = CBitcoinAddress(str(receiver_address)).to_scriptPubKey()
							txout = CMutableTxOut(REDEEM_AMOUNT*COIN, out_script_pubkey)
							tx = CMutableTransaction([txin], [txout], nLockTime = current_block)   
							sighash = SignatureHash(redeem_script, tx, 0 ,SIGHASH_ALL)
							sig = receiver_privkey.sign(sighash) + bytes([SIGHASH_ALL])
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
						with open('./Receiver/file/receiver_tx_info.json','r') as file1:
							block_info=json.load(file1)
							del block_info[str_current_block]
						with open('./Receiver/file/receiver_tx_info.json','w') as file1:
							json.dump(block_info,file1)
						lock_tx.release()

					needredeem_blockcount += 1
			except (json.JSONDecodeError,FileNotFoundError) as err2:
				lock_tx.release()
				pass
def refunded_tx(socket,msg):
	global lock_refund
	list_tx = [msg[1].decode()]
	lock_refund.acquire()
	try:   
		with open('./Receiver/file/refunded_tx.json','r') as file:
			pre_tx=json.load(file)
	except (json.JSONDecodeError,FileNotFoundError) as err:
		with open('./Receiver/file/refunded_tx.json','w') as file:
			json.dump(list_tx,file)
	if 'pre_tx' in locals().keys():
		with open('./Receiver/file/refunded_tx.json','w') as file:
			list_tx += pre_tx
			json.dump(list_tx,file)
	lock_refund.release()
	socket.send(b"I know")

options = {
	"request_for_MTree":request_for_MTree,
	"ZK_proof":send_zkproof_to_mixer,
	"refunded_tx":refunded_tx
}

function_name = {
	"request_for_MTree":'request_for_MTree',
	"ZK_proof":'send_zkproof_to_mixer',
	"refunded_tx":"refunded_tx"
}


# def main():
# 	context_sender = zmq.Context()
# 	socket_sender = context_sender.socket(zmq.REP)
# 	socket_sender.bind("tcp://127.0.0.1:5558")
# 	t = Thread(target = redeemtx)
# 	t.start()

# 	try:
# 		while True:
# 			msg = socket_sender.recv_multipart()
# 			# print "Received message %s" % msg
# 			if msg[0].decode() in options:
				
# 				print("Entering -> %s" % function_name[msg[0].decode()])
# 				options[msg[0].decode()](socket_sender, msg)
# 				print("Exiting -> %s" % function_name[msg[0].decode()])
# 				# options[msg[0]](socket, msg)

# 			else:
# 				# printf
# 				socket_sender.send(b"METHOD NOT AVAILABLE")			
# 				#Receive a multipart message as a list of bytes or Frame objects
					
# 	except KeyboardInterrupt:
# 		print("Interrupt received. Stoping ....")

# 	finally:
# 		# Clean up
# 		socket_sender.close()
# 		context_sender.term()

# if __name__ == "__main__": 
# 	main()


def worker_routine(worker_url, context=None):
	"""Worker routine"""
	context = context or zmq.Context.instance()
	# Socket to talk to dispatcher
	socket = context.socket(zmq.REP)
	socket.connect(worker_url)
	try:
		while True:
			msg = socket.recv_multipart()
			# print "Received message %s" % msg
			if msg[0].decode() in options.keys():
				
				print("Entering -> %s" % function_name[msg[0].decode()])
				options[msg[0].decode()](socket, msg)
				print("Exiting -> %s" % function_name[msg[0].decode()])
				# options[msg[0]](socket, msg)

			else:
				# printf
				socket.send(b"METHOD NOT AVAILABLE")			
				#Receive a multipart message as a list of bytes or Frame objects
					
	except KeyboardInterrupt:
		print("Interrupt received. Stoping ....")


def main():
	"""Server routine"""
	t = threading.Thread(target = redeemtx)
	t.start()

	url_worker = "inproc://workers"
	url_client = "tcp://127.0.0.1:5558"
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

if __name__ == "__main__":
	main()