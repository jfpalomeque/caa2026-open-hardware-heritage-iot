'''
Demo for a 0.91" OLED display (128x32, SSD1306) connected over I2C to the
ESP32-C3 SuperMini. Displays the device address and a counter that updates
every half second. Requires the ssd1306.py driver in the same directory.
- SDA to GPIO8
- SCL to GPIO9
'''
from machine import Pin, I2C
import time
import ssd1306


# SDA = GPIO8, SCL = GPIO9
SDA_PIN = 8
SCL_PIN = 9

# Create I2C bus
i2c = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=400000)

OLED_ADDR = 0x3c 

WIDTH = 128
HEIGHT = 32

oled = ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3c)

# Simple demo loop
counter = 0
while True:
    oled.fill(0)  # clear
    oled.text("ESP32-C3 OLED", 0, 0)
    oled.text("Addr: " + hex(OLED_ADDR), 0, 10)
    oled.text("Count: " + str(counter), 0, 20)
    oled.show()

    counter += 1
    time.sleep(0.5)