"""
Define the DataManager base class to store data from sensors over
a short time, then calculate averaged quantities over intermediate
time scales.
"""

import numpy as np
import pandas as pd
import datetime
import logging
import os.path as path

class DataManager:

    columns = ['mean', 'max', 'min']
    
    def __init__(self, output_path, sampling_period=1,
                 averaging=60, writing=5):
        self._fastbuffer = pd.Series()
        self._slowbuffer = pd.DataFrame(columns = self.columns)
        self.averaging = averaging
        self.writing = writing
        self.output_path = output_path

    def insert(self, timestamp: datetime.datetime, data: float):
        self._fastbuffer.loc[timestamp] = data
        if len(self._fastbuffer) >= self.averaging:
            self.flush_fast()

    def flush_fast(self):
        first_timestamp = self._fastbuffer.index[0]
        vals = [self._fastbuffer.__getattr__(field)() \
                for field in self.columns]
        self._slowbuffer.loc[first_timestamp, self.columns] = vals
        self._fastbuffer = pd.Series()
        if len(self._slowbuffer) > self.writing:
            self.flush_slow()

    def flush_slow(self):
        header_flag = not path.exists(self.output_path)
        with open(self.output_path, 'a') as file:
            self._slowbuffer.to_csv(file,
                                    header=header_flag)
