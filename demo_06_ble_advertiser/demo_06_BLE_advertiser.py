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