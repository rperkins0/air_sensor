"""
Downloaded 06/14/2020 from 
https://learn.adafruit.com/pm25-air-quality-sensor/python-and-circuitpython

Initializes the sensor, gets and prints readings every two seconds.
"""
import time
import board
import adafruit_si7021

# Create library object using our Bus I2C port
sensor = adafruit_si7021.SI7021(board.I2C())

while True:
    print("\nTemperature: %0.1f C" % sensor.temperature)
    print("Humidity: %0.1f %%" % sensor.relative_humidity)
    time.sleep(2)

try:
    import struct
except ImportError:
    import ustruct as struct

###
    
import serial
uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=0.25)
print("Connected to UART")

buffer = []

while True:
    data = uart.read(32)  # read up to 32 bytes
    data = list(data)
    # print("read: ", data)          # this is a bytearray type

    buffer += data

    while buffer and buffer[0] != 0x42:
        buffer.pop(0)
        print("Popping to start, remaining =", len(buffer))

    if len(buffer) > 200:
        buffer = []  # avoid an overrun if all bad data
        print("OVERRUN")
    if len(buffer) < 32:
        continue

    if buffer[1] != 0x4d:
        print("MISSING 2ND START CHARACTER")
        buffer.pop(0)
        continue

    # intbuffer = [int.from_bytes(b, 'big') for b in buffer]
    frame_len = struct.unpack(">H", bytes(buffer[2:4]))[0]
    # frame_len = struct.unpack(">H", bytes(intbuffer[2:4]))[0]
    if frame_len != 28:
        buffer = []
        print("WRONG FRAME LENGTH")
        continue

    print("UNPACKING")
    frame = struct.unpack(">HHHHHHHHHHHHHH", bytes(buffer[4:]))

    pm10_standard, pm25_standard, pm100_standard, pm10_env, \
        pm25_env, pm100_env, particles_03um, particles_05um, particles_10um, \
        particles_25um, particles_50um, particles_100um, skip, checksum = frame

    check = sum(buffer[0:30])

    if check != checksum:
        buffer = []
        print("CHECKSUM FAILED")
        continue

    print("Concentration Units (standard)")
    print("---------------------------------------")
    print("PM 1.0: %d\tPM2.5: %d\tPM10: %d" %
          (pm10_standard, pm25_standard, pm100_standard))
    print("Concentration Units (environmental)")
    print("---------------------------------------")
    print("PM 1.0: %d\tPM2.5: %d\tPM10: %d" % (pm10_env, pm25_env, pm100_env))
    print("---------------------------------------")
    print("Particles > 0.3um / 0.1L air:", particles_03um)
    print("Particles > 0.5um / 0.1L air:", particles_05um)
    print("Particles > 1.0um / 0.1L air:", particles_10um)
    print("Particles > 2.5um / 0.1L air:", particles_25um)
    print("Particles > 5.0um / 0.1L air:", particles_50um)
    print("Particles > 10 um / 0.1L air:", particles_100um)
    print("---------------------------------------")

    buffer = buffer[32:]
    # print("Buffer ", buffer)
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

i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

# Create library object on our I2C port
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)

print("SGP30 serial #", [hex(i) for i in sgp30.serial])

sgp30.iaq_init()
sgp30.set_iaq_baseline(0x8973, 0x8AAE)

elapsed_sec = 0

while True:
    print("eCO2 = %d ppm \t TVOC = %d ppb" % (sgp30.eCO2, sgp30.TVOC))
    time.sleep(1)
    elapsed_sec += 1
    if elapsed_sec > 10:
        elapsed_sec = 0
        print(
            "**** Baseline values: eCO2 = 0x%x, TVOC = 0x%x"
            % (sgp30.baseline_eCO2, sgp30.baseline_TVOC)
        )
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

