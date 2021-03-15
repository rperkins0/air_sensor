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

time_last_write = datetime.datetime.now()
write_interval = datetime.timedelta(minutes=20)
today = datetime.date.today()

while True:
    for counter in range(4):
        sensor.gather(15, sleeptime=1)
        sensor.flush_fast()
        print('solo_thcv: fast cycle complete', datetime.datetime.now())
    sensor.plot_default()
    plt.savefig(sensor.data_folder+'/thcv.png')
    if (datetime.datetime.now() - time_last_write) > write_interval:
        sensor.smartwrite()
        time_last_write = datetime.datetime.now()
        if datetime.date.today() != today:
            sensor.prune()
            today = datetime.date.today()
        
    for fignum in plt.get_fignums():
        plt.close(fignum)
