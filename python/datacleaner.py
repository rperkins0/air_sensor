"""
The data files prduced from Arduino are text files that are not optimally formatted.

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
import logging

import datatypes


logging.basicConfig(filename= '/home/rory/Arduino/python/log_dataclean.txt', 
                    level=logging.WARNING,
                    filemode='w'
                    )
#logger = logging.getLogger(__name__)

#path to original data files
data_folder = '/home/rory/Arduino/python/archive/'
#write formatted files to: 
target_folder = '/home/rory/Arduino/python/formatted/'

#for each data run type, list out the datatypes
htv_list =  [datatypes.Humidity(),
             datatypes.Temperature(),
             datatypes.TVOC(),
             datatypes.CO2(),
             ]

hcho_list = htv_list.copy()
hcho_list.append(datatypes.HCHO())

suite_list = hcho_list.copy()
mq_list =  ['Smoke', 'Alcohol', 'Methane/Propane/Butane', 'LPG', 
            'CO', 'Hydrogen', 'CO & Methane', 'Ammonia, Sulfide, Benzene']
mq_short = ['Smoke', 'Alc', 'Me/Pr/Bu', 'LPG',
            'CO', 'H', 'CO&Me', 'Amm/Sul, Benz']
for mq,short in zip(mq_list,mq_short):
    suite_list.append( datatypes.MQ(mq, shortname=short) )


#map file names to datatypes
collection_types = {'htv': htv_list,
                    'hcho': hcho_list,
                    'suite': suite_list
                    }

#regular expression to search for 'time' substring
regex_time = re.compile('[0-9][0-9]:[0-9][0-9]:[0-9][0-9]')

def get_file_list():
    import os
    import subprocess
    findfiles = subprocess.run(['ls '+data_folder],
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

    if not split_name:
        raise ValueError("File name %s cannot be parsed" % name)
    
    if split_name['dtype'] and split_name['date']:
        date = datetime.datetime.strptime(split_name['date'], '%Y%m%d')
        date = datetime.datetime.date(date) #just date; no hours/minutes ect
    else:
        raise ValueError("File name %s cannot be parsed" % name)
    return split_name['dtype'], date


def extract_timestamp(string):
    """
    Search for string of format hh:mm:ss.  Return as datetime.time object.
    """
    time_search = regex_time.search(string)
    if not time_search:
        raise ValueError('Cannot parse %s for timestamp' % string)
    h_m_s = time_search.group().split(':')
    h_m_s = [int(s) for s in h_m_s]
    return datetime.time( hour=h_m_s[0], minute=h_m_s[1], second=h_m_s[2] )


def format_datetime(day_time_string, date, start_datetime):
    """
    Replace a timestamp, previously formatted either as hh:mm:ss or
    Day:hh:mm:ss, as a datetime stamp formatted YYYY-MM-DD hh:mm:ss.
    
    day_time_string - original timestamp, sometimes with day of week
    date - date as taken from file name
    """
    change_in_format_date = datetime.date(2019,5,28)

    if date >= change_in_format_date:
        #in this case, just remove comma
        return day_time_string.replace(',', '')
    else:
        timestamp = extract_timestamp(day_time_string, date)

        
def get_csvreader(readfile, dtype):
    if dtype == 'suite':
        return csv.reader(readfile)
    else:
        return csv.reader(readfile, delimiter='\t')

    
def format_line(unformatted_data, type_list):
    """
    Match each data entry with its datatype.  Use the datatype method "convert" to format the data.

    Detect Arduino/OS garbled lines as a mismatch between number of
    fields in 'unformatted_data' and expected number.  Raise an
    IndexError
    """
    if len(unformatted_data) != len(type_list):
        raise IndexError("Line error: incorrect number of fields")
    
    z = zip( unformatted_data, type_list )
    floats = [dt.convert(s.strip()) for (s,dt) in z]
    return [str(f) for f in floats]
    

def reformat(file):
    """
    Main function.  Read a file line by line.  For properly formatted
    lines, write to a new file with proper formatting.  For improperly
    formatted lines are logged.
    """

    
    dtype, date = process_filename(file)

    try:
        type_list = collection_types[dtype]
    except:
        raise KeyError("Filename %s does not encode a valid data set")
    last_timestamp = datetime.time(hour=0, minute=0, second=0)
    
    with open(data_folder+file, 'r') as readfile:

        with open(target_folder+file, 'w') as writefile:

            csvreader = get_csvreader(readfile, dtype)

            for i,line in enumerate(csvreader):
                try:
                    timestamp = extract_timestamp(line[0])
                    if timestamp < last_timestamp:
                        #time has wrapped past midnight
                        date += datetime.timedelta(days=1)
                    now = datetime.datetime.combine(date,
                                                    timestamp)
                    datetime_str = now.strftime('%Y-%m-%d %H:%M:%S')
                    last_timestamp = timestamp

                    formatted_data = format_line(line[1:], type_list)

                    newline = '\t'.join([datetime_str]+formatted_data)+'\n'
                    writefile.write(newline)
                    logging.debug(newline)

                except IndexError as err:
                    logging.warning('Cannot parse line %s from file %s\n\t%s' % (i,file,err))
                    
                except ValueError as err:
                    logging.warning('Cannot parse line %s from file %s\n\t%s' % (i,file,err))
                    

def fileloop():
    """
    Execute reformat() for every file in data directory.
    """
    files = get_file_list()
    for file in files:
        print('Processing:', file)
        try:
            reformat(file)
        except KeyError as err:
            logging.error(err)
        except ValueError as err:
            logging.error(err)
    
                    
def test_process_filename():
    files = get_file_list()
    for f in files:
        try:
            dtype,date = process_filename(f)
        except:
            dtype = 'ERROR'
            date = 'ERROR'
        finally:
            print(f, dtype, date, sep='\t')


def test_format_datetime():
#    files = get_file_list()
    files=['suite20190725.txt']
    for file in files:
        print('\t',file)
        try:
            dtype, date = process_filename(file)
            type_list = collection_types[dtype]

            last_timestamp = datetime.time(hour=0, minute=0, second=0)
    
            with open(data_folder+file, 'r') as readfile:
                
                with open(target_folder+file, 'w') as writefile:

                    csvreader = get_csvreader(readfile, dtype)

                    for i,line in enumerate(csvreader):
                        try:
                            print(line)
                            if len(line) == len(type_list)+1:
                                timestamp = extract_timestamp(line[0])
                                if timestamp < last_timestamp:
                                    #time has wrapped past midnight
                                    date += datetime.timedelta(days=1)
                                now = datetime.datetime.combine(date,
                                                                timestamp)
                                datetime_str = now.strftime('%Y-%m-%d %H:%M:%S')
                                last_timestamp = timestamp

                                formatted_data = format_line(line[1:], type_list)

                                newline = '\t'.join([datetime_str]+formatted_data)
                                #writefile.write(newline)
                                print(newline)
                        except:
                            print('ERROR: on line', i)
        except:
            print('Skipping file', f)

if __name__=='__main__':
    fileloop()
