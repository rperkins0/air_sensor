# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

""" Example for using the SGP30 with CircuitPython and the Adafruit library
Initializes the sensor, gets and prints readings every two seconds.
"""

import time
# board automatically detects the board being used and
# imports * from appropriate board module/package
import board
# busio defines classes for each bus type, e.g. I2C for this case
import busio
import adafruit_sgp30
import adafruit_si7021
from collector import Collector


class THCV(Collector):
    """
    Collector object to handle data from a ...

    WARNING: SI7021 can create issues by "holding the master" 
    ("clock stretch"): see
    https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/i2c-clock-stretching
    https://forums.adafruit.com/viewtopic.php?p=807074
    On a Rasberry Pi 3 B V1.2, this was fixed by adding the following 
    to /boot/config.txt below the existing line: dtparam=i2c_arm=on
    dtparam=i2c_arm_baudrate=10000
    """

    data_folder = '../data/thcv'

    columns = ['temperature',
               'humidity',
               'co2',
               'tvoc'
               ]
    
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
        self.sgp30 = adafruit_sgp30.Adafruit_SGP30(self.i2c)
        self.si7021 = adafruit_si7021.SI7021(board.I2C())
        print("SGP30 serial #", [hex(i) for i in self.sgp30.serial])
        self.sgp30.iaq_init()
        # self.sgp30.set_iaq_baseline(0x8973, 0x8AAE)
        super().__init__()

        
    # def connect_si7021(self):
    #     # Create library object using our Bus I2C port
    #     self.si7021 = adafruit_si7021.SI7021(board.I2C())

    # def connect_sgp30(self):
    #     self.i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
    #     # Create library object on our I2C port
    #     self.sgp30 = adafruit_sgp30.Adafruit_SGP30(self.i2c)

        
    def get_data(self):
        """
        Query the i2c bus for both devices to get the latest data.
        """
        return (self.si7021.temperature,
                self.si7021.relative_humidity,
                self.sgp30.eCO2,
                self.sgp30.TVOC)

    def print_values(self, vals):
        print("Temperature: %0.1f C" % vals[0] )
        print("Humidity: %0.1f %%" % vals[1] )
        print("eCO2 = %d ppm \t TVOC = %d ppb" % vals[0:2] )


    def baseline(self):
        if elapsed_sec > 10:
            elapsed_sec = 0
            print(
                "**** Baseline values: eCO2 = 0x%x, TVOC = 0x%x"
                % (sgp30.baseline_eCO2, sgp30.baseline_TVOC)
                )
