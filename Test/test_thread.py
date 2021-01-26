#! /usr/bin/python3

#对于线程内的局部变量来说，线程间不影响变量的值
#线程影响全局变量的值
from threading import Thread
import time
import os
from random import randint

abspath = os.path.abspath(".") 
base = os.path.basename(abspath)
n = 0
t = []
class Sender():
	def __init__(self):		 
		self.para = base + '_' + str(randint(100000, 9999999999))

def redeemtx():
	# global n
	sender = Sender()
	n=0
	print(str(n),sender.para)
	n+=1
	time.sleep(1)
	print(str(n),sender.para)


for i in range(22):

	temp = Thread(target = redeemtx)
	t.append(temp)

	t[i].start()
for i in range(22):
	t[i].join()