#! /usr/bin/python3
import zmq
from threading import Thread
def thread_socket():
	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	socket.connect("ipc:///tmp/ZeroMixer_sender")
	socket.send(b"OK")
	msg = socket.recv()
	print(msg.decode())
t = []	
for i in range(6):
	ti = Thread(target = thread_socket)
	ti.start()
	t.append(ti)
for i in range(6):
	t[i].join()

# msg = [b"hello",b"server"]
# socket.send_multipart(msg)

# reply = socket.recv_multipart()
# for i in reply:
# 	print(i.decode())