'''
This example demonstrates how to create a BLE advertiser that broadcasts DHT22 sensor data in the manufacturer 
specific data field. The payload includes a node ID, sensor type, and the temperature and humidity readings. The advertising 
interval is randomized between 300ms and 700ms to simulate multiple devices broadcasting at different rates.
'''

import bluetooth
import struct
import time
import random
from machine import Pin
import dht

# =========================
# Config
# =========================
DEVICE_NAME = "ESP32C3_DHT01"
NODE_ID = 1
SENSOR_TYPE = 1          # 1 = DHT22 
COMPANY_ID = 0xFFFF
DHT_PIN = 21

# =========================
# BLE setup
# =========================
ble = bluetooth.BLE()
ble.active(True)

# =========================
# Sensor setup
# =========================
sensor = dht.DHT22(Pin(DHT_PIN))

# =========================
# Helpers
# =========================
def advertising_payload(name=None, manufacturer_data=None):
    payload = bytearray()

    def _append(adv_type, value):
        payload.extend(struct.pack("BB", len(value) + 1, adv_type))
        payload.extend(value)

    if name:
        _append(0x09, name.encode())   # Complete Local Name

    if manufacturer_data:
        _append(0xFF, manufacturer_data)   # Manufacturer Specific Data

    return payload


def read_dht():
    for _ in range(3):
        try:
            sensor.measure()
            temp = sensor.temperature()
            hum = sensor.humidity()
            return temp, hum
        except Exception:
            time.sleep_ms(250)
    return None, None


def make_mfg_payload(node_id, temp, hum):
    # Payload:
    # 2 bytes company ID
    # 1 byte sensor type
    # 1 byte node ID
    # 2 bytes signed temp x100
    # 2 bytes signed hum x100
    temp_i = int(temp * 100)
    hum_i = int(hum * 100)
    return struct.pack("<HBBhh", COMPANY_ID, SENSOR_TYPE, node_id, temp_i, hum_i)


# =========================
# Main loop
# =========================
print("Starting DHT22 broadcaster:", DEVICE_NAME)

while True:
    temp, hum = read_dht()

    if temp is None or hum is None:
        print("DHT22 read failed")
        time.sleep(2)
        continue

    mfg = make_mfg_payload(NODE_ID, temp, hum)
    payload = advertising_payload(name=DEVICE_NAME, manufacturer_data=mfg)

    adv_interval_ms = random.randint(300, 700)
    ble.gap_advertise(adv_interval_ms * 1000, adv_data=payload)

    print("Advertising")
    print("  Name:", DEVICE_NAME)
    print("  Node ID:", NODE_ID)
    print("  Temp:", temp, "C")
    print("  Hum :", hum, "%")
    print("  Adv interval:", adv_interval_ms, "ms")
    print("  Mfg payload:", mfg.hex())
    print()

    time.sleep(2)