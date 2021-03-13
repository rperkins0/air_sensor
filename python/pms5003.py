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
from signal import signal, SIGINT

class PMS5003():
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
        self.uart = serial.Serial("/dev/ttyS0",
                                  baudrate=9600,
                                  timeout=0.25)
        print("pms5003: Connected to UART")
        self.fastbuffer = pd.DataFrame(columns=self.columns)
        self.slowbuffer = pd.DataFrame(columns=self.columns)
        
    def get_data(self):
        """
        Enter a polling loop waiting for data to come in
        until a full message is collected.  
        Return a tuple of data.
        """

        buffer = []

        while True:
            data = self.uart.read(32)  # read up to 32 bytes
            data = list(data)

            buffer += data

            while buffer and buffer[0] != 0x42:
                buffer.pop(0)
                print("Popping to start, remaining =", len(buffer))

            if len(buffer) > 200:
                buffer = []  # avoid an overrun if all bad data
                print("OVERRUN")
            if len(buffer) < 32:
                continue

            if buffer[1] != 0x4d:
                print("MISSING 2ND START CHARACTER")
                buffer.pop(0)
                continue

            frame_len = struct.unpack(">H", bytes(buffer[2:4]))[0]
            if frame_len != 28:
                buffer = []
                print("WRONG FRAME LENGTH")
                continue

            frame = struct.unpack(">HHHHHHHHHHHHHH", bytes(buffer[4:]))

            pm10_standard, pm25_standard, pm100_standard, \
            pm10_env, pm25_env, pm100_env, \
            particles_03um, particles_05um, particles_10um, \
            particles_25um, particles_50um, particles_100um, \
            skip, checksum = frame

            check = sum(buffer[0:30])

            if check != checksum:
                buffer = []
                print("CHECKSUM FAILED")
                continue

            buffer = buffer[32:]

            return  pm10_standard, pm25_standard, pm100_standard, \
                pm10_env, pm25_env, pm100_env, \
                particles_03um, particles_05um, particles_10um, \
                particles_25um, particles_50um, particles_100um

    def gather(self, num=10):
        """
        Sit in a loop and get data and move into fastbuffer.
        """
        self.uart.reset_input_buffer()
        #while self.run:
        for i in range(num):
            dat = self.get_data()
            now = datetime.datetime.now()
            self.fastbuffer.loc[now, self.columns] = [*dat]
        
    def print_values(self, vals):
        # unpack vals
        pm10_standard, pm25_standard, pm100_standard, \
        pm10_env, pm25_env, pm100_env, \
        particles_03um, particles_05um, particles_10um, \
        particles_25um, particles_50um, particles_100um = vals

        print("Concentration Units (standard)")
        print("---------------------------------------")
        print("PM 1.0: %d\tPM2.5: %d\tPM10: %d" %
              (pm10_standard, pm25_standard, pm100_standard))
        print("Concentration Units (environmental)")
        print("---------------------------------------")
        print("PM 1.0: %d\tPM2.5: %d\tPM10: %d" % (pm10_env, pm25_env, pm100_env))
        print("---------------------------------------")
        print("Particles > 0.3um / 0.1L air:", particles_03um)
        print("Particles > 0.5um / 0.1L air:", particles_05um)
        print("Particles > 1.0um / 0.1L air:", particles_10um)
        print("Particles > 2.5um / 0.1L air:", particles_25um)
        print("Particles > 5.0um / 0.1L air:", particles_50um)
        print("Particles > 10 um / 0.1L air:", particles_100um)
        print("---------------------------------------")

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
        fullpath = self.data_folder + '/' + date_string + '.csv'
        flag = 'a' if os.path.exists(fullpath) else 'w'
        df.to_csv(fullpath,
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
        From the DateTimeIndex, get an nparray of the unique dates contained
        """
        # slowbuffer and fastbuffer have DateTimeIndex, whose 'date' method
        # returns a numpy array with datetime.date objects, e.g. just the date and
        # not the time.
        # Then use numpy unique to get the unique values.
        return np.unique( df.index.date )

    def prune(self, today=True):
        """
        Remove all date that was not taken from today.
        It is presumed that this data has already been written to file
        """
        dates = self.get_unique_dates(self.slowbuffer)
        if today:
            date_to_keep = datetime.date.today()
        else:
            date_to_keep  = dates.max()

        for d in dates:
            if d != date_to_keep:
                to_remove = self.slowbuffer.index[self.slowbuffer.index.date == d]
                self.slowbuffer.drop(to_remove, inplace=True)

        
    
