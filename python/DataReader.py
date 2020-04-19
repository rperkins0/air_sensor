"""
For use with htv*.txt files only.
e.g. data runs with SI7021 (temperature & humidity) and SGP30 (TVOC and C02)
Reads total into lists and does a single plot.
"""
import csv
import datetime
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

file='/home/rory/Arduino/python/archive/htv20190322.txt'

times = []
TVOC = []
humidity=[]
temperature=[]
co2=[]

with open(file, newline='') as csvfile:
    datareader = csv.reader(csvfile, delimiter='\t')
    for row in datareader:
        if len(row) == 5:
            times.append(datetime.datetime.strptime(row[0], '%H:%M:%S, '))
            TVOC.append(float(row[3].split(' ')[1]))
            humidity.append(float(row[1].split(' ')[1]))
            temperature.append(float(row[2].split(' ')[-1]))
            if len(row[4].split(' ')) > 1:
                co2.append(float(row[4].split(' ')[1]))
            else:
                co2.append(-1)
                #        print(row)

temperature = np.asarray(temperature)
TVOC = np.asarray(TVOC)
        
fig,ax = plt.subplots()
myFormat=DateFormatter('%H:%M:%S')
ax.xaxis.set_major_formatter(myFormat)
plt.xticks(rotation=45)
ax.plot(times,temperature)
ax.plot(times,TVOC/max(TVOC)*max(temperature)) 
fig.show()
