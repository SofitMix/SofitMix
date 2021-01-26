#! /usr/bin/python3
import zmq
import time
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("ipc:///tmp/ZeroMixer_tx")
msg = [b"test1_time1"]
socket.send_multipart(msg)

reply = socket.recv_multipart()
for i in reply:
	print(i.decode())


# time.sleep( 10 )
# msg = [b"test1_time2"]
# socket.send_multipart(msg)

# reply = socket.recv_multipart()

socket.close()
context.term()