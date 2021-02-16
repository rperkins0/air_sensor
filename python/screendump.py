# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

""" Example for using the SGP30 with CircuitPython and the Adafruit library"""

import time
# board automatically detects the board being used and
# imports * from appropriate board module/package
import board
# busio defines classes for each bus type, e.g. I2C for this case
import busio
import adafruit_sgp30
import adafruit_si7021

i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
si7021 = adafruit_si7021.SI7021(i2c)

print("SGP30 serial #", [hex(i) for i in sgp30.serial])

sgp30.iaq_init()
# sgp30.set_iaq_baseline(0x8973, 0x8AAE)

elapsed_sec = 0

while True:
    format = "Temp: {0:4.2f} \t Hum: {1:4.2f} \t" + \
        "eCO2: {2:d} ppm \t TVOC = {3:d} ppb"
    print(format.format(si7021.temperature,
                        si7021.relative_humidity,
                        sgp30.eCO2,
                        sgp30.TVOC)
          )
    time.sleep(1)
    elapsed_sec += 1
    if elapsed_sec > 10:
        elapsed_sec = 0
        print(
            "**** Baseline values: eCO2 = 0x%x, TVOC = 0x%x"
            % (sgp30.baseline_eCO2, sgp30.baseline_TVOC)
        )
