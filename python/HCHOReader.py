"""
For use with 'HCHO*.txt" files
e.g. data sets using the SI7021 (temperature & humidity) and SGP30 (TVOC and C02) 
and DFRobot Formaldehyde (HCHO) sensor.

Read a tab-separated text file written by the Arduino logger with the
ino file _____ loaded on Arduino.  Per that ino's documentation, the
Arduino was collecting data from the humidity, temperature, TVOC, CO2,
and HCHO sensors.

This python script parses the data into nparrays for plotting and processing.
"""


import csv
import datetime
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

import datatypes

file='/home/rory/Arduino/python/archive/hcho20190513.txt'

datatype_list = [datatypes.Humidity(),
                 datatypes.Temperature(),
                 datatypes.TVOC(),
                 datatypes.CO2(),
                 datatypes.HCHO()
                 ]


def unwrap_date(date_string):
    """
    Create a datetime object from a date string written in the text file.  

    Dates are typically formatted e.g. Mon:HH:MM:ss.

    Also, data is typically collected overnight, leading to "wrapping"
    issues when plotting.  The fix employed here is to incrememt the day
    to 2 if it occurs after midnight.  Better solution: 
    change Arduino code to write full date.
    """
    #year and day defaults: 1900 and 1
    ThisDateTime = datetime.datetime.strptime(date_string,
                                              '%a:%H:%M:%S, ')
    #resolve wrap by incrementing
    #day to "2" if past midnight
    if ThisDateTime.hour < 16:
        ThisDateTime=ThisDateTime.replace(day=2)

    return ThisDateTime


def parse_file(file):
    times = []
    humidity = []
    temperature = []
    TVOC = []
    co2 = []
    hcho = []
    arrays  = [humidity,temperature,TVOC,co2,hcho]
    with open(file, newline='') as csvfile:
        datareader = csv.reader(csvfile, delimiter='\t')
        for (i,row) in enumerate(datareader,1):
            try:
                ThisDateTime = unwrap_date(row[0])
                times.append(ThisDateTime)
                for (a, dt, s) in zip(arrays, datatype_list, row[1:]):
                    a.append( dt.str2float(s) )
            except BaseException as err:
                print('Could not process line ',i,':')
                print(row)
                #raise err
    return (times, humidity, temperature, TVOC, co2, hcho)

def parse_file_loadtxt(file, skip=8):
    """
    Use numpy loadtxt function to parse the data files.
    """
    #dictionary mapping columns to datatype instance
    converter_dict = {i:dt.str2float for (i,dt) in enumerate(datatype_list,1)}
        
    data = np.loadtxt( file,
                       delimiter='\t', #tab delimited
                       converters=converter_dict, #see above
                       usecols = [1,2,3,4], #all but date col
                       skiprows=skip,
                       encoding='latin1'
                       )

    dates = np.loadtxt(file,
                       delimiter='\t',
                       usecols=[0],
                       skiprows=skip,
                       encoding='latin1',
                       converters={0:unwrap_date},
                       dtype=datetime.datetime
                       )
    
    return dates, data


def parse_file_panda(file):
    """
    Use panda dataframe to parse the data files.
    """
    #dictionary mapping columns to datatype instance
    converter_dict = {i:dt.str2float for (i,dt) in enumerate(datatype_list,1)}
    converter_dict[0]=0
        
    data = np.genfromtxt( file,
                          delimiter='\t', #tab delimited
                          converters=converter_dict, #see above
                          encoding='latin1',
                          missing_values=''
                          )

    return data


(times, humidity, temperature, TVOC, co2, hcho) = parse_file(file)

fig,axarr = plt.subplots(2, 2, sharex=True)
myFormat=DateFormatter('%H:%M:%S')

DataList = [TVOC, humidity, temperature, hcho]
DataLabels = ['TVOC', 'Humidity', 'Temp', 'HCHO']

for i,ax in enumerate(axarr.flat):
    ax.xaxis.set_major_formatter(myFormat)
    ax.xaxis.set_tick_params(rotation=45)
    ax.plot(times, DataList[i])
    ax.set_title(DataLabels[i])

fig.show()
