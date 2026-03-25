'''
HC-SR04 Ultrasonic Distance Sensor Demo
This demo shows how to use the HC-SR04 ultrasonic distance sensor with an ESP32-C3.
The sensor has two main pins: TRIG (trigger) and ECHO (echo). The TRIG pin is used to send a pulse, and the ECHO 
pin is used to receive the reflected pulse.

The distance is calculated based on the time it takes for the pulse to travel to the object and back. The speed of sound is 
approximately 343 meters per second, which translates to about 29.1 microseconds per centimeter.
Make sure to connect the HC-SR04 sensor correctly:
- TRIG to GPIO20
- ECHO to GPIO21
'''

from machine import Pin, time_pulse_us
import time

# HC-SR04 connections (ESP32-C3)
TRIG = Pin(20, Pin.OUT)   # TRIG: we drive this pin to start a measurement
ECHO = Pin(21, Pin.IN)    # ECHO: sensor outputs a pulse here

def distance_cm():
    # Make sure TRIG starts low (clean pulse)
    TRIG.off()
    time.sleep_us(3)

    # Send a 10 microsecond trigger pulse
    TRIG.on()
    time.sleep_us(10)
    TRIG.off()

    # Measure how long ECHO stays HIGH (in microseconds)
    # timeout=30000us (30ms) avoids blocking forever if no echo returns
    try:
        duration = time_pulse_us(ECHO, 1, 30000)
    except OSError:
        return None  # no echo (out of range or bad reflection)

    # Convert pulse time to distance in cm
    # Divide by 2 because the sound travels out and back
    return (duration / 2) / 29.1

while True:
    d = distance_cm()
    if d is None:
        print("No echo")
    else:
        print("Distance: {:.1f} cm".format(d))

    time.sleep(0.5)  # wait between readings