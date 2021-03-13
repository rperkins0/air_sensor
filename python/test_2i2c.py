# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
"""
Testing simulataneous operation of Si7021 and SGP30 sensors on the
same I2C bus.
"""
import time
# board automatically detects the board being used and
# imports * from appropriate board module/package
import board
# busio defines classes for each bus type, e.g. I2C for this case
import busio
import adafruit_sgp30
import adafruit_si7021

i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

# Create library object on our I2C port
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)

# Create library object using our Bus I2C port
sensor = adafruit_si7021.SI7021(board.I2C())


print("SGP30 serial #", [hex(i) for i in sgp30.serial])

sgp30.iaq_init()
sgp30.set_iaq_baseline(0x8973, 0x8AAE)

elapsed_sec = 0

while True:
    print("eCO2 = %d ppm \t TVOC = %d ppb" % (sgp30.eCO2, sgp30.TVOC))
    print("\nTemperature: %0.1f C" % sensor.temperature)
    print("Humidity: %0.1f %%" % sensor.relative_humidity)
    time.sleep(2)
    elapsed_sec += 2
    if elapsed_sec > 10:
        elapsed_sec = 0
        print(
            "**** Baseline values: eCO2 = 0x%x, TVOC = 0x%x"
            % (sgp30.baseline_eCO2, sgp30.baseline_TVOC)
        )
