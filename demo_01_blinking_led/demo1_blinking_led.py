from machine import Pin
from time import sleep

led = Pin(21, Pin.OUT)
led.value(1)

for n in range(5):
  led.value(1)
  sleep(1)
  led.value(0)
  sleep(1)