import pandas as pd
import timeit

import SuitePanda
import datacleaner


def read_panda(file, type_list=None, raw=False):
    
    if type_list == None:
        #try to automatically detect data types from file name
        dtype,_ = datacleaner.process_filename(file)
        try:
            type_list = datacleaner.collection_types[dtype]
        except:
            raise KeyError("Filename %s does not encode a valid data set. Try setting 'type_list'" % file)
   
    p = pd.read_csv(datacleaner.target_folder + file,
                    delimiter='\t',
                    parse_dates=True,
                    names=[t.name for t in type_list]
                    )
    
    p.suite.datatypes = type_list
    p.suite.dtype = dtype or 'custom'
    p.suite.file= file

    if not raw:
        p.suite.cleanup()

    return p


def compare_speed():
    import SuitePanda
    
    def wrapper(func, *args, **kwargs):
        def wrapped():
            return func(*args,**kwargs)
        return wrapped

    file = 'suite20190723.txt'

    print('Running SuitePanda fileload:')
    wrapped = wrapper( SuitePanda.fileload, 'archive/'+file)
    print( timeit.timeit(wrapped,number=10) )

    print('Running read_formatted.read_panda')
    wrapped = wrapper(read_panda, file)
    print( timeit.timeit(wrapped, number=10) )
