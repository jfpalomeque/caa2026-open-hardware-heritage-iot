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
