import time
from signal import signal, SIGINT
import matplotlib.pyplot as plt
import datetime

import thcv

plt.ioff()  # turn "interactive" mode off
# so that plots do not automatically display on screen
# we just want them written to files.

sensor = thcv.THCV()

def handler(signal_received, frame):
    sensor.flush_fast()
    # sensor.write2file()
    sensor.smartwrite()
    print('Exiting THCV infinite loop;  thank you and come again')
    exit()
    
signal(SIGINT, handler)

while True:
    for counter in range(5):
        sensor.gather(5, sleeptime=1)
        sensor.flush_fast()
        print('solo_thcv: fast cycle complete', datetime.datetime.now())
    sensor.slowbuffer.plot()
    plt.savefig(sensor.data_folder+'/thcv.png')
    for fignum in plt.get_fignums():
        plt.close(fignum)
