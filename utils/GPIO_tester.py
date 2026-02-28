# ESP32-C3 Super Mini GPIO LED test (MicroPython, Thonny)
# Assumption: each GPIO drives an LED through a 330 ohm resistor to the LED anode,
# and all LED cathodes go to common GND.
#
# This will test all GPIOs on the board except GPIO2 and GPIO9.

from machine import Pin
import time

# GPIOs to test (excluded: 2 and 9)
TEST_PINS = [0, 1, 3, 4, 5, 6, 7, 8, 10, 20, 21]

ON_TIME_S = 0.25
OFF_TIME_S = 0.10
PAUSE_BETWEEN_PINS_S = 0.25

def setup_pins(pin_nums):
    pins = {}
    for n in pin_nums:
        try:
            p = Pin(n, Pin.OUT)
            p.value(0)  # start OFF
            pins[n] = p
        except Exception as e:
            print("Could not init GPIO{}: {}".format(n, e))
    return pins

def all_off(pins):
    for p in pins.values():
        p.value(0)

def chase_test(pins, loops):
    pin_nums = sorted(pins.keys())
    print("Testing GPIOs:", pin_nums)
    print("Loops:", loops)
    try:
        for _ in range(loops):
            for n in pin_nums:
                all_off(pins)
                print("GPIO{} ON".format(n))
                pins[n].value(1)
                time.sleep(ON_TIME_S)
                pins[n].value(0)
                time.sleep(PAUSE_BETWEEN_PINS_S)
        all_off(pins)
        print("Done.")
    except KeyboardInterrupt:
        all_off(pins)
        print("Stopped. All OFF.")

def blink_all(pins, times, on_s=0.2, off_s=0.2):
    try:
        for _ in range(times):
            for p in pins.values():
                p.value(1)
            time.sleep(on_s)
            for p in pins.values():
                p.value(0)
            time.sleep(off_s)
    except KeyboardInterrupt:
        all_off(pins)

pins = setup_pins(TEST_PINS)

# Quick visual check
blink_all(pins, times=5)

# Main test
chase_test(pins, loops=5)
