#! /usr/bin/python3

# LOCK_TIME = 6
# N_HASHES = 15
# HASH_LEN = 20
# TUMBLER_ADDRESS = "mzaMTvKBDiYoqkHaDz3w7AmHHETHEQKUiWs"


#一个PC上运行一个client，一个client上面可以由很多sender(Alice)，这些sender属于同一个用户。
import time

from sender_merkletree import *
from threading import Thread

from sender import *




class Sender_client():

	def __init__(self):
		pass
		# self.context_mixer = zmq.Context()
		# self.socket_mixer = self.context_mixer.socket(zmq.REQ)
		# self.socket_mixer.connect("tcp://127.0.0.1:5557")  #连到mixer
		# self.regtest = regtest
	def start(self):
		#过程执行的代码
		#1. 向mixer_server要公钥
		sender = Sender()
		receiver_pub = self.exchange(sender) #bytes
		if (not receiver_pub):
			print("Failed in exchange\n");
			return False
		
		self.generate_fundingTX(receiver_pub, sender) 
		#broadcast T_fund(A,M)
		blockcount = sender.proxy.getblockcount()
		funding_txid = sender.proxy.call("sendtoaddress", str(sender.p2sh_address), AMOUNT_FUND)
		print("fund_txid",funding_txid)
		print("corresponding h_2 is:",sender.h_2.hex())
		rawtx,blockcount = self.check_TX(sender,funding_txid,blockcount)
		while (not rawtx): #循环结束说明交易被确认
			# time.sleep(5)
			rawtx,blockcount = self.check_TX(sender,funding_txid,blockcount)
		sender.current_blockcount = blockcount  #表示上链时的blockcount
		
		t = Thread(target = self.refundtx, args = (sender,funding_txid,))
		t.start()
		msg = [funding_txid.encode(),str(sender.current_blockcount).encode(),sender.pubkey,sender.h_1,str(sender.locktime).encode()] #发送给mixer让mixer存h_1
		if (not self.send_to_mixer(sender,msg)):
			print("Failed in sending message to the mixer\n")
			return False
		print(1)
		if(not self.request_for_MTree(sender)):
			print("Failed in sending message to a receiver\n")
			# time.sleep(2) #留时间进入t线程，赎回交易。
			return False
		print(22)
		#执行完后关闭socket
		t.join()
		sender.socket_mixer.close()
		sender.context_mixer.term()
	

	def exchange(self,sender):
		#sender向mixer发送“exchange_pubkey",mixer向sender发送公钥
		#pubkey=sender.pubkey
		message = b"exchange_pubkey"
		pubkey = sender.pubkey
		msg = [message,pubkey]
		sender.socket_mixer.send_multipart(msg)
		msg = sender.socket_mixer.recv()
		#可以换成另一种秘钥生成方式，减少长度
		if len(msg) != 33:
			print(msg)		
			return False
		return msg


	def generate_fundingTX(self,receiver_pubkey, sender):
		#commit a
		h_1 = sender.h_1
		#create raw transaction
		sender_pubkey = sender.pubkey
		locktime = sender.locktime                     
		redeemScript = CScript([OP_IF,  OP_SHA256, h_1, OP_EQUALVERIFY, sender_pubkey, OP_CHECKSIG, 
							OP_ELSE, locktime, OP_CHECKLOCKTIMEVERIFY, OP_DROP,
							receiver_pubkey, OP_CHECKSIG, OP_ENDIF])       #输入输出都是bytes
		script_pub_key = redeemScript.to_p2sh_scriptPubKey()            #bytes
		p2sh_address = CBitcoinAddress.from_scriptPubKey(script_pub_key)  #string
		address_info = [p2sh_address, redeemScript]
		sender.p2sh_address = p2sh_address
		sender.redeemScript = redeemScript
	    

	def check_TX(self,sender,txid,blockcount):
		#check whether this tx is confirmed
		current_count = sender.proxy.call("getblockcount")
		if blockcount!=current_count:
			blockhash = sender.proxy.call("getblockhash",current_count)
			try:
				rawtx = sender.proxy.call("getrawtransaction",txid,0,blockhash)
				return rawtx, current_count
			except bitcoin.rpc.InvalidAddressOrKeyError as e:
				return 0, current_count
		else:
			return 0,current_count
			#表示交易已经被确定

	def refundtx(self,sender,funding_txid):
	#right 278
		# time.sleep(4)
		print("entering refundtx")
		context_mixer = zmq.Context()
		socket_mixer = context_mixer.socket(zmq.REQ)
		socket_mixer.connect("tcp://127.0.0.1:5557") 
		print("currentblock:",sender.proxy.call("getblockcount"))
		print("locktime:",sender.locktime)
		while True:
			blockcount = sender.proxy.call("getblockcount")
			if blockcount == sender.locktime:
				return
			if sender.refund_flag == True:				
				redeem_script = sender.redeemScript
				script_pub_key = redeem_script.to_p2sh_scriptPubKey()
				#自动定位utxo
				hextx = sender.proxy.call("gettransaction",funding_txid)['hex']
				raw_txid = x(hextx)
				temp_tx = CTransaction.deserialize(raw_txid)
				tx = CMutableTransaction.from_tx(temp_tx)
				if tx.vout[0].scriptPubKey == script_pub_key:
					vout = 0
				else:
					vout =1 
				txid = lx(funding_txid)
				txin = CMutableTxIn(COutPoint(txid,vout))
				out_script_pubkey = CBitcoinAddress(str(sender.refunding_address)).to_scriptPubKey()
				txout = CMutableTxOut(REFUND_AMOUNT*COIN, out_script_pubkey)
				tx = CMutableTransaction([txin], [txout])   
				sighash = SignatureHash(redeem_script, tx, 0 ,SIGHASH_ALL)
				sig = sender.privkey.sign(sighash) + bytes([SIGHASH_ALL])
				txin.scriptSig = CScript([sig, sender.a.encode(), OP_TRUE, redeem_script])
				while True:
					try:
						spend_txid = sender.proxy.call("sendrawtransaction", b2x(tx.serialize()))
						break
					except VerifyError as e:
						time.sleep(3)
				# print("refund_tx",spend_txid)
				print("refund corresponding tx is:", funding_txid)
				refund_info = [b"refund_tx",sender.a.encode(),funding_txid.encode()]
				
				socket_mixer.send_multipart(refund_info)
				msg = socket_mixer.recv()
				print(msg)
				return					
			# time.sleep(3)


	def send_to_mixer(self,sender,msg):
		#msg = [txid,block_count,sender.pubkey,sender.h_1,sender.locktime]
		message = b"send_message_to_mixer"
		msg.insert(0,message)
		sender.socket_mixer.send_multipart(msg)
		msg = sender.socket_mixer.recv()
		if msg != b"correct_tx":
			print(msg)
			return False
		return True


	def request_for_MTree(self,sender):
		
		message = b"request_for_MTree"	
		context_receiver = zmq.Context()
		socket_receiver = context_receiver.socket(zmq.REQ)
		socket_receiver.connect("tcp://localhost:5558")
		socket_receiver.send(message)
		# MTree = [root,hashlist]
		print(7)
		MTree = socket_receiver.recv_multipart()
		print(8)
		#生成Merkle proof
		root = MTree[0]
		leaves = MTree[1:]

		try:
			assert sender.h_1 in leaves
		except AssertionError as e1:
			print("the hash value is not in this Merkle tree")
			return False

		mt = MerkleTools()
		mt.add_leaf(leaves)
		mt.make_tree()
		try:
			assert mt.get_merkle_root() == root.hex()
		except AssertionError as e2:
			print("Merkel root is uncorrect")
			return False
	    
		num = leaves.index(sender.h_1)
		proof = mt.get_proof(num)
		

		#打印
		# print(sender.a)
		# print(sender.b)
		# print(sender.h_1.hex())
		# print(sender.h_2.hex())
		# print(sender.g.hex())
		# print(root.hex())
		# print(proof)

		#转为C++处理
		context_c = zmq.Context()
		socket_c = context_c.socket(zmq.REQ)
		socket_c.connect("ipc:///tmp/ZeroMixer_sender")
		msg_to_c = [sender.a,sender.b,sender.h_1.hex(),sender.h_2.hex(),sender.g.hex(),root.hex(),proof]

		socket_c.send_json(msg_to_c)
		print(2)
		pi = socket_c.recv()
		print(3)
		socket_c.close()
		context_c.term()
		proof_to_receiver = [b"ZK_proof",sender.b.encode(),sender.g,sender.h_2,pi]
		socket_receiver.send_multipart(proof_to_receiver)
		
		print(4)
		reply_from_receiver = socket_receiver.recv_multipart()
		print(5)
		print(reply_from_receiver)
		socket_receiver.close()
		context_receiver.term()

		# [funding_txid, blockcount, h2, receiver_pubkey, mixer_pubkey, LOCKTIME] or "TX already redeemed by sender"
		# 验证reply，不对立马赎回
	 	# 1.验redeemscript对不对
	 	# 2.验在timelock快过期时，交易在不在链上，可通过h2关联交易
		print("len of reply from receiver is:",len(reply_from_receiver))
		if len(reply_from_receiver) != 6:	
			
			print(reply_from_receiver[0].decode())
			#如果检验不正确，使redeem_flag = True,表示立刻赎回
			sender.refund_flag = True
			print(11)
			return False
		
		blockcount = int(reply_from_receiver[1])
		proxy = bitcoin.rpc.Proxy()
		# print(blockcount)
		# print("blockcount:",proxy.call("getblockcount"))
		blockhash = proxy.call("getblockhash",blockcount)
		try:
			#tx on chain
			rawtx = proxy.call("getrawtransaction",reply_from_receiver[0].decode(),True,blockhash)
		except bitcoin.rpc.InvalidAddressOrKeyError as e:
			print("cannot find corresponding TX")
			sender.refund_flag = True
			print(12)
			return False 

		redeem_script = CScript([OP_IF, OP_SHA256, reply_from_receiver[2], OP_EQUALVERIFY, reply_from_receiver[4], OP_CHECKSIG, 
								OP_ELSE, int(reply_from_receiver[5]), OP_CHECKLOCKTIMEVERIFY, OP_DROP,
								reply_from_receiver[3], OP_CHECKSIG, OP_ENDIF])
		script_pub_key = redeem_script.to_p2sh_scriptPubKey()
		#can redeem by receiver
		try:
			assert rawtx['vout'][0]['scriptPubKey']['hex']==b2x(script_pub_key) or rawtx['vout'][1]['scriptPubKey']['hex']==b2x(script_pub_key)
			
		except AssertionError as e:
			print("TX is not correct") 
			sender.refund_flag = True
			print(13)
			return False
		return True

def main():

	#循环多次，建多个sender_client
	sender_client=Sender_client()
	# time_start=time.time()
	# sender_client.start()
	t=[]
	for i in range(400):
		ti= Thread(target = sender_client.start)
		ti.start()
		t.append(ti)
	# 每一次start，产生一个新的sender,使用多线程
	for i in range(400):
		t[i].join()
	# time_end=time.time()
	# print('totally cost: ',time_end-time_start)


if __name__ == '__main__':
	main()

