#! /usr/bin/python3
from mixer import *
import time



def generate_fundingTX(proxy,b, g, h2, receiver_pubkey, mixer_pubkey):
    print("entering genetate fundingtx")
    global lock_mixer_redeemscript
    locktime = LOCKTIME + proxy.getblockcount()

    redeemScript = CScript([OP_IF,  OP_SHA256, h2, OP_EQUALVERIFY, mixer_pubkey, OP_CHECKSIG, 
                                OP_ELSE, locktime, OP_CHECKLOCKTIMEVERIFY, OP_DROP,
                                receiver_pubkey, OP_CHECKSIG, OP_ENDIF])      
    script_pub_key = redeemScript.to_p2sh_scriptPubKey()
    P2SH_address = CBitcoinAddress.from_scriptPubKey(script_pub_key)
    print("current_time:",str(proxy.call("getblockcount")))
    print("locktime:",locktime)
    # address_info={"redeemScript":redeemScript,"P2SH_address":p2sh_address}
    amount = AMOUNT_FUND
    blockcount = proxy.getblockcount()
    funding_txid = proxy.call("sendtoaddress", str(P2SH_address),amount)
    print("fund_txid",funding_txid)
    # 存redeemscript信息
    info = [funding_txid, b.decode(), h2.hex(), receiver_pubkey.hex(), mixer_pubkey.hex(),locktime]
    to_receiver_info = [funding_txid.encode(), mixer_pubkey, str(locktime).encode()]

    redeemscript_info = {g.hex() : info} #以后赎回用
    print("g is:",g.hex())
    
    lock_mixer_redeemscript.acquire()
    # print('I got lock_mixer_redeemscript---%s'%(time.ctime()))
    try:   
        #可换成.pem后缀 
        with open('./Mixer/file/mixer_redeemscript_info.json','r') as file:
            tx_info=json.load(file)
    except (json.JSONDecodeError,FileNotFoundError) as err:
        with open('./Mixer/file/mixer_redeemscript_info.json','w') as file:
            json.dump(redeemscript_info,file)
    if 'tx_info' in locals().keys():
        with open('./Mixer/file/mixer_redeemscript_info.json','w') as file:
            new_info=dict(tx_info,**redeemscript_info)
            json.dump(new_info,file)
    lock_mixer_redeemscript.release()
    # print('I release lock_mixer_redeemscript---%s'%(time.ctime()))
    print("exist genetate fundingtx")
    return blockcount, to_receiver_info


def check_TX(proxy,txid,blockcount):
    #check whether this tx is confirmed
    current_count = proxy.call("getblockcount")
    # print(blockcount)
    # print(current_count)
    # time.sleep(2)
    if blockcount!=current_count:
        blockhash = proxy.call("getblockhash",current_count)

        try:
            rawtx = proxy.call("getrawtransaction",txid,0,blockhash)
            return rawtx, current_count
        except bitcoin.rpc.InvalidAddressOrKeyError as e:
            return 0, current_count
    else:
        return 0,current_count


def validation_Mproof(socket,msg):
    global lock_listg, lock_code
    e=5
    if len(msg) != e:
        socket.send(error(len(msg), e))
        print("Exiting -> %s" % msg[0])
        return 
    #msg: correct Mproof, b,g,h_2,receiver.pubkey
    #检查是否已经被sender赎回
    proxy = bitcoin.rpc.Proxy()
    try:  
        lock_listg.acquire() 
        # print('I got lock_listg---%s'%(time.ctime()))

        lock_code.acquire()
        # print(' mixer_tx_server %s is runing' % os.getpid())

        with open('./Mixer/file/list_g.json','r') as file:
            list_g=json.load(file)
            lock_listg.release()
        
            if msg[2].hex() not in list_g:  #说明没有被sender赎回      
                mixer_pubkey = get_btc_key()
                blockcount, reply = generate_fundingTX(proxy, msg[1],msg[2],msg[3],msg[4],mixer_pubkey)
                lock_code.release()

                rawtx,blockcount = check_TX(proxy,reply[0].decode(),blockcount)
                # print(blockcount)
                # print(rawtx)
                #到这里了
                print("h_2 in fund tx is:",msg[3].hex())
                while (not rawtx): #循环结束说明交易被确认
                    # time.sleep(5)
                    rawtx,blockcount = check_TX(proxy, reply[0].decode() ,blockcount)
                current_blockcount = blockcount  #表示上链时的blockcount
                print(4)
                #[correct Mproof, blockcount, funding_txid, blockcount, LOCKTIME]
                reply.insert(1,str(current_blockcount).encode())
                socket.send_multipart(reply)

            else:
                
                lock_code.release()
                socket.send(b"TX already redeemed by sender")
                print("TX already redeemed by sender")

    except (json.JSONDecodeError,FileNotFoundError) as err:
        lock_code.release()
        lock_listg.release()
        print(err)
        mixer_pubkey = get_btc_key()
        blockcount, reply = generate_fundingTX(proxy, msg[1],msg[2],msg[3],msg[4],mixer_pubkey)
        rawtx,blockcount = check_TX(proxy,reply[0].decode(),blockcount)
        print(blockcount)
        print(rawtx)
        print(5)
        while (not rawtx): #循环结束说明交易被确认
            # time.sleep(5)
            rawtx,blockcount = check_TX(proxy, reply[0].decode() ,blockcount)
        print(6)
        current_blockcount = blockcount  #表示上链时的blockcount
        #[funding_txid,blockcount, mixer_pubkey, LOCKTIME]
        reply.insert(1,str(current_blockcount).encode())
        socket.send_multipart(reply)

option = {
    "correct Mproof":validation_Mproof
}

# def main():

#     context_to_c = zmq.Context()
#     socket_to_c = context_to_c.socket(zmq.REP)
#     socket_to_c.bind("ipc:///tmp/ZeroMixer_Mixer")
#     t = []


#     try:
#         while True:
#             print(1)
#             msg = socket_to_c.recv_multipart()
#             print(2)
#             # print "Received message %s" % msg
#             # if msg[0].decode() in local_option:
#             #     print("Entering -> validation_Mproof")
#             #     ti = Thread(target = local_option[msg[0].decode()], args = (socket_to_c, msg,))
#             #     ti.start()
#             #     t.append(ti)
#             if msg[0].decode() in option.keys():
#                 print("Entering -> validation_Mproof")
#                 option[msg[0].decode()](socket_to_c, msg)
#                 print("Exiting -> validation_Mproof")
                

#             else:
#                 # printf
#                 socket_to_c.send(b"METHOD NOT AVAILABLE")
#     except KeyboardInterrupt:
#         print ("Interrupt received. Stoping ....")
#     finally:
#         # Clean up
#         socket_to_c.close()
#         context_to_c.term()


# if __name__ == "__main__":
#     main()

def worker_routine(worker_url, context=None):
    
    """Worker routine"""
    context = context or zmq.Context.instance()
    # Socket to talk to dispatcher
    socket = context.socket(zmq.REP)
    socket.connect(worker_url)
    try:
        while True:
            msg = socket.recv_multipart()
            print("Enter mixer_tx_server.py")
            # print "Received message %s" % msg
            if msg[0].decode() in option.keys():
                
                print("Entering -> validation_Mproof")
                option[msg[0].decode()](socket, msg)
                print("Exiting -> validation_Mproof")
                # options[msg[0]](socket, msg)

            else:
                # printf
                socket.send(b"METHOD NOT AVAILABLE")         
                #Receive a multipart message as a list of bytes or Frame objects
                    
    except KeyboardInterrupt:
        print("Interrupt received. Stoping ....")


def main2():
    """Server routine"""
    print(' mixer_tx_server %s is runing' % os.getpid())
    url_worker = "inproc://workers"
    url_client = "ipc:///tmp/ZeroMixer_Mixer"
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
#     main()