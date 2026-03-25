'''
BLE scanner that listens for the "ESP32C3_BEACON" device and decodes
the temperature and humidity values from the manufacturer data in the
advertisement. Use together with BLE_beacon_DHT22_advertiser.py.
'''
import bluetooth
import struct
import time

ble = bluetooth.BLE()
ble.active(True)

TARGET_NAME = "ESP32C3_BEACON"

_IRQ_SCAN_RESULT = 5
_IRQ_SCAN_DONE = 6

def decode_name(adv_data):
    i = 0
    while i + 1 < len(adv_data):
        length = adv_data[i]
        if length == 0:
            break
        adv_type = adv_data[i + 1]
        if adv_type in (0x08, 0x09):
            return bytes(adv_data[i + 2:i + 1 + length]).decode("utf-8", "ignore")
        i += 1 + length
    return None

def decode_manufacturer_data(adv_data):
    i = 0
    while i + 1 < len(adv_data):
        length = adv_data[i]
        if length == 0:
            break
        adv_type = adv_data[i + 1]
        if adv_type == 0xFF:
            return adv_data[i + 2:i + 1 + length]
        i += 1 + length
    return None

def bt_irq(event, data):
    if event == _IRQ_SCAN_RESULT:
        addr_type, addr, adv_type, rssi, adv_data = data
        name = decode_name(adv_data)

        if name == TARGET_NAME:
            mfg = decode_manufacturer_data(adv_data)
            if mfg and len(mfg) >= 6:
                company_id, temp_i, hum_i = struct.unpack("<Hhh", mfg[:6])
                temp = temp_i / 100
                hum = hum_i / 100
                print("Beacon:", name, "| RSSI:", rssi, "| Temp:", temp, "C | Hum:", hum, "%")

    elif event == _IRQ_SCAN_DONE:
        print("Scan complete\n")

ble.irq(bt_irq)

while True:
    print("Scanning for 5 seconds...")
    ble.gap_scan(5000, 30000, 30000)
    time.sleep(6)