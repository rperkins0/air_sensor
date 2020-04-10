import csv
import datetime
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

file='/home/rory/Arduino/python/archive/hcho20190513.txt'

times = []
TVOC = []
humidity=[]
temperature=[]
co2=[]
hcho=[]

with open(file, newline='') as csvfile:
    datareader = csv.reader(csvfile, delimiter='\t')
    for row in datareader:
        if len(row) == 6:
            #this creates a datetime object
            #however, year and day are defaulted to
            #1900 and 1 respectively
            #This creates wrap issues when plotting
            ThisDateTime = datetime.datetime.strptime(row[0],
                                                      '%a:%H:%M:%S, ')
            #resolve wrap windows by incrementing
            #day to "2" if past midnight
            #this is a hack
            #should write full date
            if ThisDateTime.hour < 16:
#                dummy=1
                ThisDateTime=ThisDateTime.replace(day=2)

            times.append(ThisDateTime)
            TVOC.append(float(row[3].split(' ')[1]))
            humidity.append(float(row[1].split(' ')[1]))
            temperature.append(float(row[2].split(' ')[-1]))
            if len(row[4].split(' ')) > 1:
                co2.append(float(row[4].split(' ')[1]))
            else:
                co2.append(-1)
                #        print(row)
            hcho.append(float(row[5].split(' ')[1]))

temperature = np.asarray(temperature)
TVOC = np.asarray(TVOC)
        
fig,axarr = plt.subplots(2, 2, sharex=True)#plt.subplots()
myFormat=DateFormatter('%H:%M:%S')

DataList = [TVOC, humidity, temperature, hcho]
DataLabels = ['TVOC', 'Humidity', 'Temp', 'HCHO']

for i,ax in enumerate(axarr.flat):
    ax.xaxis.set_major_formatter(myFormat)
    ax.xaxis.set_tick_params(rotation=45)
    ax.plot(times, DataList[i])
    ax.set_title(DataLabels[i])


# axarr[0,0].plot(times, TVOC)
# axarr[0,0].set_title('TVOC')
# axarr[0,1].plot(times,humidity)
# plt.gca().set_title('Humidity')
# axarr[1,0].plot(times,temperature)
# plt.gca().set_title('Temp')
# axarr[1,1].plot(times,hcho)
# plt.gca().set_title('HCHO')
#ax.plot(times,hcho)
#ax.plot(times,TVOC/max(TVOC)*max(temperature)) 
fig.show()