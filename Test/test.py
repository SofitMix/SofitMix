#! usr/bin/python3

from lock1 import *
from lock2 import *

w1 = threading.Thread(target=test1)

w2 = threading.Thread(target=test2)

w1.start()

w2.start()

w1.join()

w2.join()