"""
26 May 2019

Read characters from an Arduino that has been programmed to output humidity, temperature, TVOC, and CO2.
   /home/rory/Arduinosi7021_sgp30/si7021_sgp30.ino
This python code does serial reads, writes to file prepending with a timestamp, and parses the data for real-time plotting.

17 Mar 2019
Updating to write full date, instead of just hour, minute, second.  
"""

import serial
import time
import datetime
import os
import csv
import numpy as np 
import re
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

# NOTE the user must ensure that the next line refers to the correct comm port
ser = serial.Serial("/dev/ttyACM0", 115200)

file = open('htv.txt', 'w')

numLoops = 24*2400
n = 0
waitingForReply = False

fig, ax = plt.subplots()
myFormat = DateFormatter('%a:%H:%M:%S')

TVOCArray = np.array([])
times=[]

while n < numLoops:
  charout = '0'
  stringout = ''
  #10 is the integer representation of a new line \n
  #so loop through an entire line
  while ord(charout) != 10:
    charout = ser.read()
    stringout = stringout + charout.decode("utf-8")
    
  now = datetime.datetime.now()
  print(now.strftime("%Y-%m-%d %H:%M:%S, ")+', ' + stringout)
  file.write(now.strftime("%a:%H:%M:%S")+', ' + stringout)
  file.flush()
  os.fsync(file.fileno())

  if n > 6:
    #break line of text into list of number strings
    datastrings = re.findall('[0-9.]+', stringout)
    if len(datastrings) == 5:
      (humidity,
       temperature,
       TVOC,
       dummy,
       C02,) = [float(i) for i in datastrings]
      #convert each string into float, then upack
      #into individual variables

      times.append(now)
      TVOCArray = np.append( TVOCArray, TVOC )

      ax.clear()
      ax.plot(times, TVOCArray )
      ax.xaxis.set_major_formatter(myFormat)
      plt.xticks(rotation=45)
      plt.ion()
      fig.show()
      plt.pause(.001)

  n=n+1
  
ser.close
file.close()
