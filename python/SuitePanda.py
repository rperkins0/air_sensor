"""
An API extension of pandas.DataFrame to bind plotting and data cleanup
methods with a new namespace of the DataFrame object.
"""

import csv
import datetime
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pandas as pd

import datacleaner

@pd.api.extensions.register_dataframe_accessor('suite')
class suite(object):
    """
    Inheriting from pandas.DataFrame is not straightforward.  I have since learned the proper way.
    However, the pandas website recommends this "extension" methodology, which creates a new 
    namespace within DataFrames where the user can write their own methods and bound data.  

    NOTE:
    Within the 'suite' extension, the DataFrame is accessed via "self._obj"
    """

    #lookup dictionary of max values to allow for each datatype
    MaxVal = {'Humidity':100.,
              'Temperature':100.,
              'TVOC':10000., 
              'CO2':10000., 
              'HCHO':10., 
              'Smoke':5., 
              'Alcohol':5.,
              'Methane/Propane/Butane':1., 
              'LPG':1.0, 
              'CO':1.0, 
              'Hydrogen':1.0, 
              'CO & Methane':1.0,
              'Ammonia, Sulfide, Benzene':5.
              }

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


    def generic_grid_plot(self, rows, cols,
                          types_to_plot,
                          format='%m-%d %H:%M',
                          ):
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


    def cleanup_adc(self):
        """ 
        Remove all ADC channels for days on which ADC was busted.
        On dates 07/10, 07/11, 07/12, and another cluster from
        07/27 through 07/31.
        This only impacts the "MQ" sensors.
        """
        ADC_channel_names = datacleaner.mq_list
        if not set(ADC_channel_names).isdisjoint( set(self._obj.columns) ): #see if mq sensors are in data set
            self._obj.loc['07/10/2019':'07/12/2019', ADC_channel_names] = np.nan
            self._obj.loc['07/27/2019 16:25':'07/31/2019', ADC_channel_names] = np.nan

    def cleanup_blips(self):
        """
        Remove anomolously high data points.
        Arduino occasionally 'hiccups' for a data point.
        """
        for name,val in self.MaxVal.items():
            if name in self._obj.columns:
                self._obj.loc[self._obj[name] > val, name] = np.nan

    def cleanup_temperature_low(self):
        """
        The temperature sensor or Arduino occasionally returns false results ("blips")
        that are too low to be physical.  These "blips" would be missed by the 
        remove_blips() function above.

        TODO: remove blips by searching for anomolous changes in data, rather than by
        high/low values.
        """
        if 'Temperature' in self._obj.columns:
            self._obj.loc[self._obj['Temperature'] < 40, 'Temperature'] = np.nan

    def cleanup(self):
        self.cleanup_adc()
        self.cleanup_blips()
        self.cleanup_temperature_low()
            
    def test_change_data(self):
        self._obj['Humidity'][0:3] = np.nan
                              
