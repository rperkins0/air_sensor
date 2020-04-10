
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

def dec10(data, time):
    decimated = np.zeros((1, data.shape[1]))
    t_decimated = [datetime.datetime.now()]

    DecimateData = np.zeros(( data.shape[0]//10, 13 ))
    DecimateTime = [None]*(data.shape[0]//10)
    print(DecimateTime)
    print(range(0,len(DecimateTime)//10*10,10))
    for i in range(0,len(DecimateTime)):
      #by default, sum acts on first dimension only
      DecimateData[i,:] = sum(data[10*i:10*(i+1),:])/10
      DecimateTime[i] = time[10*i+5]
    decimated = np.append( decimated,
                           DecimateData,
                           axis=0)
    t_decimated.extend(DecimateTime)
    return decimated, t_decimated
