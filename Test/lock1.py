#! usr/bin/python3
from threadlock import *

def test1():
	global lock1
	print(' %s is runing' % os.getpid())
	lock1.acquire()
	print("enter lock1")
	time.sleep(5)
	print("exist lock1")
	lock1.release()
	
