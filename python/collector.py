"""
Downloaded 06/14/2020 from 
https://learn.adafruit.com/pm25-air-quality-sensor/python-and-circuitpython
Converted to a class on 2021-02-27
"""

try:
    import struct
except ImportError:
    import ustruct as struct  
import serial
import pandas as  pd
import numpy as np
import datetime
from time import sleep
import os

class Collector():
    """
    Class to communicate with a PMS5003 air-quality sensor over UART
    """

    data_folder = '../data/pms5003'
    
    columns = ['pm10_standard',
               'pm25_standard',
               'pm100_standard', 
               'pm10_env',
               'pm25_env',
               'pm100_env',
               'particles_03um',
               'particles_05um',
               'particles_10um',
               'particles_25um',
               'particles_50um',
               'particles_100um']
            
    def __init__(self):
        self.fastbuffer = pd.DataFrame(columns=self.columns)
        self.slowbuffer = pd.DataFrame(columns=self.columns)
        
    def get_data(self):
        """
        Take a single data point from all sensors.
        """
        raise NotImplementedError

    def clear_device_buffer(self):
        pass
    
    def gather(self, num=10, sleeptime=0):
        """
        Sit in a loop and get data and move into fastbuffer.
        """
        self.clear_device_buffer()
        #while self.run:
        for i in range(num):
            dat = self.get_data()
            now = datetime.datetime.now()
            self.fastbuffer.loc[now, self.columns] = [*dat]
            sleep(sleeptime)
        
    def print_values(self, vals):
        raise NotImplementedError

    def flush_fast(self):
        if len(self.fastbuffer)>0:
            mean = self.fastbuffer.mean()
            time = self.fastbuffer.index[0]
            self.slowbuffer.loc[time] = mean
            self.fastbuffer = pd.DataFrame(columns=self.columns)

    def flush_slow(self):
        self.write2file()
        self.slowbuffer = pd.DataFrame(columns=self.columns)
                    
    def write2file(self):
        # get today's date as a string
        today = datetime.date.today()  # creates a 'date' object
        today_string = today.strftime('%Y-%m-%d')  # creates string
        # format = YYYY-MM-DD

        fullpath = self.data_folder + '/' + today_string + '.csv'

        flag = 'a' if os.path.exists(fullpath) else 'w'
        
        self.slowbuffer.to_csv(fullpath,
                               sep='\t',
                               header=False,
                               mode=flag)

    def write2file2(self, df: pd.DataFrame, date: datetime.date):
        date_string = date.strftime('%Y-%m-%d')
        full_path = self.data_folder + '/' + date_string + '.csv'
        flag = 'a' if os.path.exists(full_path) else 'w'
        df.to_csv(full_path,
                  sep='\t',
                  header='False',
                  mode=flag)

    def smartwrite(self):
        dates = self.get_unique_dates( self.slowbuffer )
        for d in dates:
            self.write2file2( self.slowbuffer[ self.slowbuffer.index.date == d ],
                              d)
        
    @staticmethod
    def get_unique_dates(df: pd.DataFrame):
        """
        From the DateTimeIndex, get an ndarray of the unique dates contained
        """
        # slowbuffer and fastbuffer have DateTimeIndex, whose 'date' method
        # returns a numpy array of datetime.date objects, e.g. just date no time.
        # Numpy unique gives the unique values.
        return np.unique( df.index.date )

    def prune(self, today=True):
        """
        Remove data from slowbuffer that was not taken today.
        It is presumed that this data has already been written to file
        """
        dates = self.get_unique_dates(self.slowbuffer)
        if today:
            date2keep = datetime.date.today()
        else:
            date2keep  = dates.max()

        for d in dates:
            if d != date_to_keep:
                to_remove = self.slowbuffer.index[self.slowbuffer.index.date == d]
                self.slowbuffer.drop(to_remove, inplace=True)

        
    
