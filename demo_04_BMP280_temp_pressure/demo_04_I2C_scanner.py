'''
I2C Scanner for finding devices on the I2C bus. This code initializes the I2C bus and scans for connected devices,
printing their addresses. 
It also reads the chip ID from the BMP280 sensor to confirm it's connected properly.
'''

from machine import Pin, I2C

# I2C pins for ESP32-C3 SuperMini
SDA_PIN = 8
SCL_PIN = 9
# I2C address of the sensor
ADDR = 0x76

# Initialize I2C bus (100 kHz)
i2c = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=100000)

# Check connected devices
print("I2C scan:", [hex(a) for a in i2c.scan()])

# Read chip ID to confirm sensor
chip_id = i2c.readfrom_mem(ADDR, 0xD0, 1)[0]
print("Chip ID:", hex(chip_id))