import bluetooth
import struct
import time
from machine import Pin
import dht

ble = bluetooth.BLE()
ble.active(True)

sensor = dht.DHT22(Pin(21))
DEVICE_NAME = "ESP32C3_BEACON"

def read_dht():
    for _ in range(3):
        try:
            sensor.measure()
            t = sensor.temperature()
            h = sensor.humidity()
            return t, h
        except Exception:
            time.sleep_ms(250)
    return None, None

def advertising_payload(name=None, manufacturer_data=None):
    payload = bytearray()

    def _append(adv_type, value):
        payload.extend(struct.pack("BB", len(value) + 1, adv_type))
        payload.extend(value)

    if name:
        _append(0x09, name.encode())

    if manufacturer_data:
        _append(0xFF, manufacturer_data)

    return payload

while True:
    temp, hum = read_dht()

    if temp is None or hum is None:
        temp_i = -999
        hum_i = -999
    else:
        temp_i = int(temp * 100)
        hum_i = int(hum * 100)

    # Manufacturer data format:
    # 2 bytes company id placeholder + 2 bytes temp + 2 bytes hum
    mfg = struct.pack("<Hhh", 0xFFFF, temp_i, hum_i)

    payload = advertising_payload(name=DEVICE_NAME, manufacturer_data=mfg)
    ble.gap_advertise(200_000, adv_data=payload)  # 200 ms

    print("Advertising temp:", temp, "C | hum:", hum, "%")
    time.sleep(2)