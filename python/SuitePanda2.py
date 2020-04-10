import csv
import datetime
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pandas as pd

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

def fileload(file, verbose=False):
    DataRows=[]
    times=[]
    withPath='/home/rory/Arduino/python/' + file

    with open(withPath, newline='') as csvfile:
        datareader = csv.reader(csvfile, delimiter=',')
        for row in datareader:
            if len(row) == 14:
                Temp={}
                #Attempt to parse line.  In case of error (Arduino
                #blip), then skip line
                try:
                    #These columns have text description in addition to data
                    for i in range(1,6):
                        #split by spaces and take third value
                        DataVal = row[i].split(' ')[2]
                        #convert to float and store in dictionary
                        Temp[DataNames[i-1]] = float(DataVal.strip())

                    #These columns should be just data
                    for i in range(6,14):
                        Temp[DataNames[i-1]]= float(row[i].strip())

                    DataRows.append(Temp)
                    ThisDateTime = datetime.datetime.strptime(row[0],
                                                          '%Y-%m-%d %H:%M:%S')
                    #only appends time if previous lines successful
                    times.append(ThisDateTime)
                except ValueError:
                    if verbose == True:
                        print('ERROR: Data not formatted properly,'+
                              'skipping line')
                        print(','.join(row))
                    else:
                        pass
                except IndexError:
                    if verbose == True:
                        print('ERROR: indexing problem, skipping line')
                        print(','.join(row))
                    else:
                        pass

    try:
        df = pd.DataFrame(DataRows, columns=DataNames)
        df.set_index(pd.Index(times), inplace=True)
    except IndexError:
        print('Index error in making panda!')
        df = {}
    return df


@pd.api.extensions.register_dataframe_accessor('suite')
class suite(object):

    def __init__(self, pandas_obj):
        # if type(pandas_obj) == pd.core.frame.DataFrame:
        #     self._obj = pandas_obj
        # elif type(pandas_obj) == str:
        #     self._obj = self._fileload(pandas_obj)
        self._obj = pandas_obj

    def testmutability(self, col, val):
        #result: can indeed change values
        self._obj[col] = val

    def testreplacement(self):
        #result: cannot reassign self._obj to an new DataFrame
        self._obj = pd.DataFrame({ "World's":[1],
                                   "dumbest":[2],
                                   "panda":[3] })

    def fileload(self, file):
        DataRows=[]
        times=[]
        withPath='/home/rory/Arduino/python/' + file

        with open(withPath, newline='') as csvfile:
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
        return df

    def addfile(self,file):
        Temp = fileload(file)
        print("temp loaded with length", len(Temp))
        Temp2 = self._obj.append(Temp)
        print("temp2 loaded with length", len(Temp2))
        self._obj.update(Temp2)

    def SuitePlot(self, format='%M-%D %H:%M'):
        fig,axarr = plt.subplots(3, 4, sharex=True)
        myFormat=DateFormatter(format)

        PlotNames = DataNames.copy()
        PlotNames.remove('Hydrogen')

        avg = self._obj.mean()
        std = self._obj.std()
        
        for i,ax in enumerate(axarr.flat):
            ax.xaxis.set_major_formatter(myFormat)
            ax.xaxis.set_tick_params(rotation=45)
            #ax.plot(times, DataList[i])
            #ax.set_title(DataLabels[i])
            self._obj.plot(y=PlotNames[i], ax=ax, style=',')
            TimeRange = [self._obj.index[0],self._obj.index[-1]]
            ax.plot( TimeRange, 
                     np.ones(2)*avg[PlotNames[i]],
                     color='r',
                     linewidth=0.5)
            ax.plot( TimeRange, 
                     np.ones(2)*(avg[PlotNames[i]]+std[PlotNames[i]]),
                     linestyle='dashed',
                     color='r',
                     linewidth=0.5)
            ax.plot( TimeRange, 
                     np.ones(2)*(avg[PlotNames[i]]-std[PlotNames[i]]),
                     linestyle='dashed',
                     color='r',
                     linewidth=0.5)

        plt.subplots_adjust(left=0.1,
                            right=0.95,
                            top=0.95,
                            bottom=0.15)
        fig.show()