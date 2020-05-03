class Datatype(object):
    """
    Abstract base class for the different types of data produced by
    the air sensors.
    """
    def __init__(self,
                 name = 'Data',
                 shortname=None,
                 sensor='Unknown',
                 breakoutboard='Unknown',
                 vendor='Unknown',
                 unit='?'
                 ):                 
        self.name = name
        self.shortname = shortname or name #default to name
        self.sensor = sensor
        self.breakoutboard = breakoutboard
        self.vendor = vendor
        self.unit = unit

    def str2float(self, string):
        """
        Method to convert the string reported by Arduino to a float.
        Must be implmented in each child.
        """
        raise NotImplementedError

    def convert(self, string):
        try:
            return self.str2float(string)
        except:
            raise ValueError("Conversion error: datatype %s cannot convert '%s'" % (self.name,string)) 

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name
        
class Temperature(Datatype):
    def __init__(self):
        super().__init__(name = 'Temperature',
                         shortname = 'Temp'
                         sensor = 'SI7021',
                         breakoutboard='SI7021',
                         vendor='Adafruit',
                         unit = 'F'
                         )

    def str2float(self, string):
        number_string = string.split(': ')[1]
        return float(number_string)

    
class Humidity(Datatype):
    def __init__(self):
        super().__init__(name='Humidity',
                         shortname='Hum',
                         sensor = 'SI7021',
                         breakoutboard='SI7021',
                         vendor='Adafruit',
                         unit = '%'
                         )

    def str2float(self, string):
        number_string = string.split(': ')[1]
        return float(number_string)


class TVOC(Datatype):
    def __init__(self):
        super().__init__(name = 'TVOC',
                         sensor = 'SGP30',
                         breakoutboard='?',
                         vendor='Adafruit',
                         unit = 'ppb'
                         )

    def str2float(self, string):
        number_string = string.split(' ')[1]
        return float(number_string)

class CO2(Datatype):
    def __init__(self):
        super().__init__(name='CO2',
                         sensor = 'SGP30',
                         breakoutboard='?',
                         vendor='Adafruit',
                         unit = 'ppm'
                         )

    def str2float(self, string):
        number_string = string.split(' ')[1]
        return float(number_string)

class HCHO(Datatype):
    def __init__(self):
        super().__init__(name = 'HCHO',
                         breakoutboard='?',
                         vendor='DFRobot',
                         unit = 'ppm'
                         )

    def str2float(self, string):
        number_string = string.split(' ')[1]
        return float(number_string)


class MQ(Datatype):
    def __init__(self, name, **kwargs):
        super().__init__(name = name,
                         breakoutboard='?',
                         vendor='DFRobot',
                         unit = 'ARB',
                         **kwargs
                         )

    def str2float(self, string):
        number_string = string.strip()
        return float(number_string)
