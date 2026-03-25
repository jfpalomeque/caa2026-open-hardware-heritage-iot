'''
BMP280 Temperature and Pressure Sensor Demo
This demo shows how to use the BMP280 sensor to read temperature and pressure values with an ESP32-C3 SuperMini.
The BMP280 is a popular sensor for measuring atmospheric pressure and temperature. 
It communicates over I2C, so we will use the I2C interface of the ESP32-C3 to read data from the sensor.
Make sure to connect the BMP280 sensor correctly:
- SDA to GPIO8
- SCL to GPIO9
'''

from machine import Pin, I2C
import time
from bmp280 import BMP280

# I2C pins for ESP32-C3 SuperMini
SDA_PIN = 8
SCL_PIN = 9
# I2C address of the sensor
ADDR = 0x76

# Initialize I2C bus (100 kHz)
i2c = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=100000)


# Create sensor object
sensor = BMP280(i2c=i2c, address=ADDR)

# Continuous reading loop
while True:
    temp, pres = sensor.values
    print("Temp:", temp, "Pressure:", pres)
    time.sleep(2)
