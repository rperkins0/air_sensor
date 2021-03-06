import csv
import datetime
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pandas as pd

file='/home/rory/Arduino/python/archive/suite20190607.txt'

times = []
TVOC = []
humidity=[]
temperature=[]
co2=[]
hcho=[]

DataRows=[]

DataNames = [ 'Humidity',
              'Temperature',
              'TVOC',
              'CO2',
              'HCHO',
              'Smoke',
              'Alcohol',
              'Methane/Propane/Butane',
              'LPG',
              'CO',
              'Hydrogen',
              'CO & Methane',
              'Ammonia, Sulfide, Benzene']

with open(file, newline='') as csvfile:
    datareader = csv.reader(csvfile, delimiter=',')
    for row in datareader:
        if len(row) == 14:
            Temp={}
            try:
                #These columns have text description in addition to data
                for i in range(1,6):
                    #split by spaces and take second value
                    DataVal = row[i].split(' ')[2]
                    #convert to float and store in dictionary
                    Temp[DataNames[i-1]] = float(DataVal.strip())
                
                #These columns should be just data
                for i in range(6,14):
                    Temp[DataNames[i-1]]= float(row[i].strip())
                    #print(DataNames[i-1])
                    #print(float(row[i].strip()))
                
                DataRows.append(Temp)
                ThisDateTime = datetime.datetime.strptime(row[0],
                                                      '%Y-%m-%d %H:%M:%S')
                times.append(ThisDateTime)
            except ValueError:
                print('ERROR: Data not formatted properly, skipping line')
                print(','.join(row))
            except IndexError:
                print('ERROR: indexing problem, skipping line')
                print(','.join(row))

try:
    df = pd.DataFrame(DataRows, columns=DataNames)
    df.set_index(pd.Index(times), inplace=True)
except IndexError:
    print('Index error in making panda!')
    df = {}

#Make 3x4 plot
fig,axarr = plt.subplots(3, 4, sharex=True)
myFormat=DateFormatter('%H:%M')

PlotNames = DataNames
PlotNames.remove('Hydrogen')

for i,ax in enumerate(axarr.flat):
    #ax.xaxis.set_major_formatter(myFormat)
    #ax.xaxis.set_tick_params(rotation=45)
    #ax.plot(times, DataList[i])
    #ax.set_title(DataLabels[i])
    df.plot(y=PlotNames[i], ax=ax)
    ax.xaxis.set_major_formatter(myFormat)

plt.subplots_adjust(left=0.1,
                    right=0.95,
                    top=0.95,
                    bottom=0.10)
fig.show()
