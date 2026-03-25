'''
This code demonstrates how to blink an LED connected to GPIO 21 on the ESP32-C3 SuperMini. 
It initializes the pin as a digital output and toggles it on and off with a one-second delay
between states, creating a blinking effect. The LED will blink five times before the program ends.
'''
from machine import Pin
from time import sleep

# Initialize GPIO 21 as a digital output driving the LED.
led = Pin(21, Pin.OUT)
led.value(1)

# Blink the LED five times with one second on/off intervals.
for n in range(5):
  led.value(1)
  sleep(1)
  led.value(0)
  sleep(1)