"""
Data files from Arduino are text files that are not optimally formatted.

This module provides functions to cleanup the data and write into new files
for faster and cleaner loading into analysis/plotting routines.

Specific issues addressed:
1) Use full date+time on each line (previously just time).
2) Remove Arduino hiccups (lines with missing data).
3) Add header with date range and data types.
4) Remove text that makes data human-readable.

"""

import numpy as np
import pandas as pd
import datetime
import re
import csv

import datatypes

#path to original data files
data_folder = '/home/rory/Arduino/python/archive/'
#write formatted files to: 
target_folder = '/home/rory/Arduino/python/formatted/'

#for each data run type, list out the datatypes
htv_list =  [datatypes.humidity(),
             datatypes.temperature(),
             datatypes.TVOC(),
             datetypes.CO2(),
             ]

hcho_list = htv_list.copy()
hcho_list.append(datatypes.HCHO())

#map file names to datatypes
collection_types = {'htv': htv_list,
                    'hcho': hcho_list
                    }

def get_file_list():
    import os
    import subprocess
    findfiles = subprocess.run(['ls '+folder],
                               stdout=subprocess.PIPE,
                               shell=True)
    fullpaths = findfiles.stdout.decode('utf-8').split('\n')
    return [os.path.basename(p) for p in fullpaths]


def process_filename(name):
    """
    Given a file name, extract the type of data inside and the start
    date of the collection.
    """
    split_name = re.search(r'(?P<dtype>.*)(?P<date>[0-9]{8,8})(?P<suffix>.*)',
                           name)  

    if split_name['dtype'] and split_name['date']:
        date = datetime.datetime.strptime(split_name('date'), %Y%m%d)
        date = datetime.datetime.date(date) #just date; no hours/minutes ect
    else:
        raise ValueError("File name cannot be parsed.")
    return split_name['dtype'], date
    
def format_datetime(day_time_string, date):
    """
    Replace a timestamp, previously formatted either as hh:mm:ss or
    Day:hh:mm:ss, as a date-time stamp formatted YYYY-MM-DD hh:mm:ss.
    """
    pass

def reformat(file):
    """
    Main function.  Read a file line by line.  For properly formatted
    lines, write to a new file with proper formatting.  For improperly
    formatted lines are logged.
    """

    dtype, date = process_filename(file)
    
    with open(data_folder+file, 'r') as readfile:
        with open(target_folder+file, 'w') as writefile:
            csvreader = csv.reader(readfile, delimiter='\t')
            for line in csvreader