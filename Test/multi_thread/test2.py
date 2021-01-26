#! /usr/bin/python3
import zmq
import time
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("ipc:///tmp/ZeroMixer_tx")
msg = [b"test2"]
socket.send_multipart(msg)

reply = socket.recv_multipart()
for i in reply:
	print(i.decode())


socket.close()
context.term()