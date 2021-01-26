#! /usr/bin/python3

from mixer_server import *

from mixer_tx_server import *

# w1 = multiprocessing.Process(target=main1)

# w2 = multiprocessing.Process(target=main2)

w1 = threading.Thread(target=main1)

w2 = threading.Thread(target=main2)

w1.start()

w2.start()

w1.join()

w2.join()