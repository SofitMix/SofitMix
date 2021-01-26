#! usr/bin/python3
from threadlock import *
from lock1 import test1
def test2():
	global lock1
	print(' %s is runing' % os.getpid())
	lock1.acquire()
	print("enter lock2")
	time.sleep(5)
	print("exist lock2")
	lock1.release()

# w1 = Process(target=test1)

# w2 = Process(target=test2)

# w1.start()

# w2.start()

# w1.join()

# w2.join()


	
