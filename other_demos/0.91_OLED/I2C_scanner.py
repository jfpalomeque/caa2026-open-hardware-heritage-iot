from machine import Pin, I2C

# I2C pins for ESP32-C3 SuperMini
SDA_PIN = 8
SCL_PIN = 9


# Initialize I2C bus (100 kHz)
i2c = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=100000)

devices = i2c.scan()
print("I2C devices found:")

for d in devices:
    print([hex(d)])
    chip_id = i2c.readfrom_mem(d, 0xD0, 1)[0]
    print("Chip ID:", hex(chip_id))