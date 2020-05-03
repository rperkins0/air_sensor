"""
 17 Mar 2019

Code to receive ascii lines from an Arduino, prepend a timestamp (HH:MM:ss), and write to a file.
"""

import serial
import time
import datetime
import os

# NOTE the user must ensure that the next line refers to the correct comm port
ser = serial.Serial("/dev/ttyACM0", 115200)

file = open('htv.txt', 'w')

numLoops = 8000
n = 0
waitingForReply = False

while n < numLoops:
  charout = '0'
  stringout = ''
  while ord(charout) != 10:
    charout = ser.read()
    stringout = stringout + charout.decode("utf-8")

  now = datetime.datetime.now()
  print(now.strftime("%H:%M:%S")+', '+stringout)
  file.write(now.strftime("%H:%M:%S")+', '+stringout)
  file.flush()
  os.fsync(file.fileno())
  n=n+1
  
ser.close
file.close()
