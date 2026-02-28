# ESP32-C3 SuperMini + DHT22 on pin 21
# BLE advertising only: broadcasts temperature + humidity in Manufacturer Data
# No connections needed. Any scanner can see it (nRF Connect, LightBlue, etc.)

import time
import struct
from machine import Pin
import dht
import ubluetooth

sensor = dht.DHT22(Pin(21))
ble = ubluetooth.BLE()
ble.active(True)

def _append(payload: bytearray, ad_type: int, value: bytes) -> None:
    payload.extend(struct.pack("BB", len(value) + 1, ad_type))
    payload.extend(value)

def make_adv_payload(name: str, temp_c: float, hum_pc: float) -> bytes:
    # Encode:
    # temp_x100: signed int16 (C * 100)
    # hum_x100 : unsigned uint16 (% * 100)
    temp_x100 = int(temp_c * 100)
    hum_x100 = int(hum_pc * 100)

    # Manufacturer Specific Data:
    # [Company ID (2 bytes, little endian)] + [type (1 byte)] + [temp int16] + [hum uint16]
    # Company ID 0xFFFF is "testing" (not a real company). Fine for demos.
    mfg = struct.pack("<HbhH", 0xFFFF, 0x01, temp_x100, hum_x100)

    p = bytearray()
    _append(p, 0x01, b"\x06")                 # Flags
    _append(p, 0x09, name.encode())           # Complete Local Name
    _append(p, 0xFF, mfg)                     # Manufacturer Specific Data
    return bytes(p)

ADV_INTERVAL_US = 250000  # 250 ms

name = "C3DHT"

print("Starting BLE broadcast. Scan for:", name)

last_good = (0.0, 0.0)

while True:
    try:
        sensor.measure()
        t = sensor.temperature()
        h = sensor.humidity()
        last_good = (t, h)
    except Exception as e:
        # DHT22 can fail sometimes; keep advertising last known values
        t, h = last_good
        print("DHT read error:", e)

    adv = make_adv_payload(name, t, h)

    # Update advertising data by restarting advertising with new payload
    try:
        ble.gap_advertise(None)  # stop
    except:
        pass

    ble.gap_advertise(ADV_INTERVAL_US, adv_data=adv)

    print("Broadcasting: T={:.1f}C H={:.1f}%".format(t, h))

    # DHT22 should be read about every 2 seconds or slower
    time.sleep(2)