#! usr/bin/python3
import os
from multiprocessing import Process,Lock
import threading
import time

lock = Lock()
lock1 = threading.Lock()