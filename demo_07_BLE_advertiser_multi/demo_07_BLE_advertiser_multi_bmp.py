import bluetooth
import struct
import time
import random
from machine import Pin, I2C
from bmp280 import BMP280

# =========================
# Config
# =========================
DEVICE_NAME = "ESP32C3_BMP01"
NODE_ID = 2
SENSOR_TYPE = 2 # 2 = BMP280
COMPANY_ID = 0xFFFF

I2C_ID = 0
SDA_PIN = 8
SCL_PIN = 9
ADDR = 0x76

# =========================
# BLE setup
# =========================
ble = bluetooth.BLE()
ble.active(True)

# =========================
# Sensor setup
# =========================
i2c = I2C(I2C_ID, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=100000)
sensor = BMP280(i2c=i2c, address=ADDR)

# =========================
# Helpers
# =========================
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


def parse_float(value):
    # Converts values like "24.6C" or "1007.8hPa" to float
    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, bytes):
        value = value.decode()

    value = str(value).strip()
    cleaned = ""

    for ch in value:
        if ch in "0123456789.-":
            cleaned += ch

    return float(cleaned)


def read_bmp():
    try:
        temp, pressure = sensor.values
        temp = parse_float(temp)
        pressure = parse_float(pressure)
        return temp, pressure
    except Exception as e:
        print("BMP read error:", e)
        return None, None


def make_mfg_payload(node_id, temp, pressure):
    # 2 bytes company ID
    # 1 byte sensor type
    # 1 byte node ID
    # 2 bytes signed temp x100
    # 4 bytes signed pressure x100
    temp_i = int(temp * 100)
    pressure_i = int(pressure * 100)
    return struct.pack("<HBBhi", COMPANY_ID, SENSOR_TYPE, node_id, temp_i, pressure_i)


# =========================
# Main loop
# =========================
print("Starting BMP280 broadcaster:", DEVICE_NAME)

while True:
    temp, pressure = read_bmp()

    if temp is None or pressure is None:
        print("BMP280 read failed")
        time.sleep(2)
        continue

    mfg = make_mfg_payload(NODE_ID, temp, pressure)
    payload = advertising_payload(name=DEVICE_NAME, manufacturer_data=mfg)

    adv_interval_ms = random.randint(300, 700)
    ble.gap_advertise(adv_interval_ms * 1000, adv_data=payload)

    print("Advertising")
    print("  Name:", DEVICE_NAME)
    print("  Node ID:", NODE_ID)
    print("  Temp:", temp, "C")
    print("  Pressure:", pressure, "hPa")
    print("  Adv interval:", adv_interval_ms, "ms")
    print("  Mfg payload:", mfg.hex())
    print()

    time.sleep(2)