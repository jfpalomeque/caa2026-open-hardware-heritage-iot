'''
ESP-NOW sender that reads temperature and humidity from a DHT22 on GPIO21
and sends the values to a specific receiver MAC address. The data is sent
as a comma-separated string: "temp,hum,counter".
Note: this script may not work on some ESP32-C3 SuperMini boards due to
antenna issues. Tested with models that have an external antenna port.
'''
# This script doesnt work on some esp32-C3 Supermini (probably due issues with antenna.
# I used one of the new models, with external antenna port
import network
import espnow
import time
import dht
from machine import Pin

# DHT22 on GPIO21
sensor = dht.DHT22(Pin(21))

# TTGO T-Display receiver MAC
RECEIVER_MAC = b'\x84\xcc\xa8`\x14\x84'

# Wi-Fi STA mode required for ESP-NOW
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()

# ESP-NOW setup
e = espnow.ESPNow()
e.active(True)
e.add_peer(RECEIVER_MAC)

n = 0
while True:
    try:
        sensor.measure()
        t = sensor.temperature()
        h = sensor.humidity()

        msg = "{:.1f},{:.1f},{}".format(t, h, n)  # "temp,hum,counter"
        e.send(RECEIVER_MAC, msg)

        print("Sent:", msg)
        n += 1

    except Exception as ex:
        print("Error:", ex)

    time.sleep(2)