import time
from signal import signal, SIGINT
import matplotlib.pyplot as plt
import datetime

import pms5003

plt.ioff()  # turn "interactive" mode off
# so that plots do not automatically display on screen
# we just want them written to files.

sensor = pms5003.PMS5003()

def handler(signal_received, frame):
    sensor.uart.close()
    sensor.flush_fast()
    # sensor.write2file()
    sensor.smartwrite()
    print('Exiting PMS5003 infinite loop;  thank you and come again')
    exit()
    
signal(SIGINT, handler)

while True:
    for counter in range(5):
        sensor.gather(20)
        sensor.flush_fast()
        print('solo_pms5003: fast cycle complete', datetime.datetime.now())
    sensor.slowbuffer.plot(y=sensor.columns[6:])
    plt.savefig(sensor.data_folder+'/pms5003.png')
    for fignum in plt.get_fignums():
        plt.close(fignum)
