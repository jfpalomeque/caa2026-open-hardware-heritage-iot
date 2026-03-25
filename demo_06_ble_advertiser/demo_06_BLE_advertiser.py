'''
This example demonstrates how to create a BLE advertiser using the ESP32-C3's Bluetooth Low Energy (BLE) 
capabilities. The device will broadcast its presence with a specified name, allowing other BLE-enabled devices 
to discover it.

To run this example, you will need to have the ESP32-C3 set up with MicroPython and the necessary Bluetooth 
libraries. The code initializes the BLE module, sets up an advertising payload with the device name, and starts 
advertising. The device will continue to advertise until it is stopped or reset.

You can use a BLE scanner (like the one in demo_06_BLE_advertiser_scanner.py) to discover 
the advertised device and see its name and other details.
'''
import bluetooth
import struct
import time

ble = bluetooth.BLE()
ble.active(True)

DEVICE_NAME = "ESP32C3_advertiser"

def advertising_payload(name=None):
    payload = bytearray()

    def _append(adv_type, value):
        payload.extend(struct.pack("BB", len(value) + 1, adv_type))
        payload.extend(value)

    if name:
        _append(0x09, name.encode())  # Complete Local Name

    return payload

payload = advertising_payload(name=DEVICE_NAME)

ble.gap_advertise(100_000, adv_data=payload)  # 100 ms
print("Advertising as:", DEVICE_NAME)

while True:
    time.sleep(1)