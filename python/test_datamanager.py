import datamanager
import time
from signal import signal, SIGINT
import datetime


dm = datamanager.DataManager('deleteme.txt', averaging=10)

def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    dm.flush_slow()
    exit(0)

signal(SIGINT,handler)

for i in range(1000):
    dm.insert(datetime.datetime.now(), i)
    print(i, len(dm._fastbuffer))
    time.sleep(.1)

dm._slowbuffer
