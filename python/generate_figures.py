"""
This set of functions provides an overview of the data over the entire
duration it was taken.  Results are typically averaged over each data set, which
lasts for several hours each day.  
"""

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pandas as pd
import subprocess
import logging
import seaborn as sns

import datacleaner
import read_formatted


#import logging after read_formatted, otherwise read_formatted (which calls
#datacleaner) will override logging settings
log_report = logging.getLogger(__name__)
log_report.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
if not log_report.handlers:
    fh = logging.FileHandler('/home/rory/Arduino/python/log_report.txt',
                             mode='w')
    fh.setLevel(logging.DEBUG)
    log_report.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    log_report.addHandler(sh)


folderpath = '/home/rory/Arduino/python/formatted'

plt.style.use('bmh')

def get_files():
    """
    Returns a list of formatted data files.
    /home/rory/Arduino/python/formatted/
    """
    findfiles = subprocess.run(['ls '+folderpath+'/*'],
                            stdout=subprocess.PIPE,
                            shell=True)
    fullpaths = findfiles.stdout.decode('utf-8').split('\n')
    return [p.split('/')[-1] for p in fullpaths if p]


def generate_figures():
    for f in get_files():
        print(f)
        try:
            p = read_formatted.read_panda(f)
            fig,_ = p.suite.SuitePlot(format='%H:%M')
            if len(p.columns) > 5:
                fig.set_size_inches(10,6)
            plt.savefig('/home/rory/Arduino/python/png/' +\
                        f.split('.')[0] +'.png')
            del p
            plt.close('all')
        except Exception as err:
            print(err)


def generate_report():
    """
    Compute average, standard of deviation, and maximum for each data set.
    Log results.
    """
    pd.set_option('display.precision', 2)
    for f in get_files():
        try:
            p = read_formatted.read_panda(f)
            
            x = pd.DataFrame({'avg':p.mean(),
                              'std':p.std(),
                              'max':p.max()
                              }
                             )
            x=x.transpose()
            
            #change column names to shorter versions
            dtype, date = datacleaner.process_filename(f)
            try:
                type_list = datacleaner.collection_types[dtype]
                x.columns = [d.shortname for d in type_list]
            except Exception as err:
                print(err)
                log_report.error(err)
            
            log_report.info(x)
            del p
        except Exception as err:
            print(err)
            log_report.error(err)


def get_stat(stat):
    """
    Loop through data files, compute stat for each data type,
    return a DataFrame indexed by date.
    """
    result = pd.DataFrame()

    for f in get_files():
        p = read_formatted.read_panda(f)
        series = getattr(p, stat)()
        dataframe = pd.DataFrame(series)

        _, date = datacleaner.process_filename(f)
        dataframe.columns = [date]
        
        result = result.append( dataframe.transpose() )

    return result
    

def plot_datatype(datatype, mean, std, maxi):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    
    ax.xaxis.set_major_formatter(DateFormatter('%m-%d'))
    ax.xaxis.set_tick_params(rotation=45)

    mean.plot(y=datatype, ax=ax, rot=45)
    mean_plus_std = mean[datatype]+std[datatype]
    mean_plus_std.plot(ax=ax,
                       label='',
                       color='blue',
                       alpha=0.5,
                       linewidth=0.5)
    mean_minus_std = mean[datatype]-std[datatype]
    mean_minus_std.plot(ax=ax,
                        label='',
                        color='blue',
                        linewidth=0.5,
                        alpha=0.5)
    maxi.plot(y=datatype, ax=ax)
    ax.fill_between(mean.index,
                    mean_plus_std,
                    mean_minus_std,
                    alpha=0.2,
                    color='cyan'
                    )
    return fig,ax
    

def generate_report_plot():
    mean = get_stat('mean')
    std  = get_stat('std')
    maxi = get_stat('max')

    for x in [mean,std,maxi]:
        x.sort_index(inplace=True)
        log_report.debug(x)

    datatypes = [(dt.name, dt.shortname) for dt in datacleaner.suite_list]
    for dt,sn in datatypes:
        fig,ax = plot_datatype(dt, mean, std, maxi)
        plt.savefig('/home/rory/Arduino/python/png/' +\
                    'trend_' + sn +'.png')

    return mean, std, maxi


if __name__=="__main__":
    generate_report_plot()
