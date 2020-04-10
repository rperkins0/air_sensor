import csv
import datetime
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pandas as pd

@pd.api.extensions.register_dataframe_accessor('suite')
class suite(object):
    def __init__(self,pandas_obj):
        self._obj = pandas_obj

    def header(self):
        print('yesh')
        self._obj.head()
