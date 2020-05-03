import matplotlib.pyplot as plt
import pandas as pd
import subprocess
import logging

import read_formatted

#import logging after read_formatted, otherwise read_formatted (which calls
#datacleaner) will override logging settings
#TODO: create different logging instances


def get_files():
    findfiles = subprocess.run(['ls /home/rory/Arduino/python/formatted/*'],
                            stdout=subprocess.PIPE,
                            shell=True)
    fullpaths = findfiles.stdout.decode('utf-8').split('\n')
    return [p.split('/')[-1] for p in fullpaths]


def generate_figures():
    for f in get_files():
        print(f)
        try:
            p = read_formatted.read_panda(f)
            p.suite.SuitePlot(format='%H:%M')
            plt.savefig(f.split('.')[0] +'.png')
            del p
            plt.close('all')
        except Exception as err:
            print(err)


def generate_report():
    log_report = logging.getLogger('log_report')
    log_report.setLevel(logging.INFO)
    #temporary crutch
    #clear all file handlers that were set globally in datacleaner.py
    for h in log_report.handlers:
        log_report.removeHandler(h)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('/home/rory/Arduino/python/log_report.txt',
                             mode='w')
    fh.setLevel(logging.INFO)
    log_report.addHandler(fh)

    pd.set_option('display.precision', 2)
    for f in get_files():
        try:
            p = read_formatted.read_panda(f)
            x = pd.DataFrame({'avg':p.mean(),
                              'std':p.std(),
                              'max':p.max()
                              }
                             )
            log_report.info(x.transpose())
            del p
        except Exception as err:
            print(err)
            log_report.error(err)


if __name__=="__main__":
    generate_report()

