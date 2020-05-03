"""
1) Functions to read a data file into a panda.DataFrame
2) Use panda api to create a custom set of methods.  Plotting routines are defined here.

NOTE: I have read that inheriting from pandas is a difficult task and that, for my purposes, using the "extension" API is easier.

"""

import csv
import datetime
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pandas as pd

#data names, in the order they are stored
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
    """
    Read a data file that has been written straight from an Arduino (no extra formatting).
    Create & return a data frame by appending line by line.
    
    A typical data line is:
    2019-05-28 11:17:51, Humidity: 46.32, Temp: 77.05, TVOC: 0.00 ppb, eCOtwo: 400.00 ppm, HCHO: 0.542 ppm, 1.52, 0.46, 0.09, 0.30, 0.54, 0.16, 0.21, 4.91
    """
    DataRows=[]
    times=[]
    withPath='/home/rory/Arduino/python/' + file

    with open(withPath, newline='') as csvfile:
        datareader = csv.reader(csvfile, delimiter=',')
        count= 0
        for row in datareader:
            
            if len(row) == 14:
                Temp={}
                #Attempt to parse line.
                #In case of error (Arduino blip), skip line
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
                except ValueError as err:
                    if verbose == True:
                        print('ERROR: Data not formatted properly,'+
                              'skipping line')
                        print(','.join(row))
                        print(row)
                        print(Temp)
                    else:
                        pass
                except IndexError:
                    if verbose == True:
                        print('ERROR: indexing problem, skipping line')
                        print(','.join(row))
                        print(row)
                        print(Temp)
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
    """
    This was an attempt to "extend" the DataFrame class.
    Ideally, I wanted to inherit from DataFrame and keep my custom "Suite"-specific methods bound with the DataFrame.
    Unfortunately, inheriting from pandas is not straightforward.  I have since learned the proper way.
    However, the pandas website recommends this "extension" methodology, which creates a new namespace within DataFrames
    where the user can write their own methods and bound data.  BUT, YOU CANNOT MODIFY the DataFrame, or 
    it requires methods beyond my knowledge. 

    I eventually moved the 'fileload' method out of this extension and into a function (see above).  The only
    method left in the extension is the SuitePlot method.  

    NOTES:
    Within the 'suite' extension, the DataFrame is access via "self._obj"
    """
    def __init__(self, pandas_obj, datatypes=None):
        self._obj = pandas_obj
        self.datatypes=datatypes

    def testmutability(self, col, val):
        #result: can indeed change values
        self._obj[col] = val

    def testreplacement(self):
        #result: cannot reassign self._obj to an new DataFrame
        self._obj = pd.DataFrame({ "World's":[1],
                                   "dumbest":[2],
                                   "panda":[3] })

    def test_attribute(self):
        print(self.datatypes)
        
    def SuitePlot(self, format='%m-%d %H:%M'):
        columns = self._obj.columns
        N = len(self._obj.columns)
        if N > 12:
            types_to_plot = [n for n in columns if n != 'Hydrogen']
            return self.generic_grid_plot(3, 4, types_to_plot, format=format)
        elif N > 4:
            return self.generic_grid_plot(2, 3, columns, format=format)
        else:
            return self.generic_grid_plot(2, 2, columns, format=format)


    def generic_grid_plot(self, rows,cols,types_to_plot, format='%m-%d %H:%M'):
        """
        Define a rows x cols subplot grid, then perform a plot for
        each datatype in types_to_plot
        """
        fig,axarr = plt.subplots(rows, cols, sharex=True)
        myFormat=DateFormatter(format)

        avg = self._obj.mean()
        std = self._obj.std()

        for n,ax in zip(types_to_plot, axarr.flat):
            ax.xaxis.set_major_formatter(myFormat)
            ax.xaxis.set_tick_params(rotation=45)
            self._obj.plot(y=n, ax=ax, style=',')
            TimeRange = [self._obj.index[0],self._obj.index[-1]]
            ax.plot( TimeRange, 
                     np.ones(2)*avg[n],
                     color='r',
                     linewidth=0.5)
            ax.plot( TimeRange, 
                     np.ones(2)*(avg[n]+std[n]),
                     linestyle='dashed',
                     color='r',
                     linewidth=0.5)
            ax.plot( TimeRange, 
                     np.ones(2)*(avg[n]-std[n]),
                     linestyle='dashed',
                     color='r',
                     linewidth=0.5)

        plt.subplots_adjust(left=0.1,
                            right=0.95,
                            top=0.95,
                            bottom=0.15)
        fig.show()
        return fig,axarr

