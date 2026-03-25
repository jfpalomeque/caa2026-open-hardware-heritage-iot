'''
This is a BLE scanner that listens for advertisements from the multi-sensor ESP32C3 advertiser demo. It filters for devices 
whose name starts with "ESP32C3" and attempts to decode the manufacturer data payload according to the format defined in 
the advertiser demo.
'''

import bluetooth
import binascii
import struct
import time

ble = bluetooth.BLE()
ble.active(True)

_IRQ_SCAN_RESULT = 5
_IRQ_SCAN_DONE = 6

seen = {}

NAME_PREFIX = "ESP32C3"

SENSOR_TYPE_DHT22 = 1
SENSOR_TYPE_BMP280 = 2

def format_mac(addr):
    return ":".join("{:02X}".format(b) for b in bytes(addr))


def decode_name(adv_data):
    adv_data = bytes(adv_data)
    i = 0
    while i + 1 < len(adv_data):
        length = adv_data[i]
        if length == 0:
            break

        adv_type = adv_data[i + 1]

        if adv_type in (0x08, 0x09):
            try:
                return bytes(adv_data[i + 2:i + 1 + length]).decode("utf-8", "ignore")
            except Exception:
                return None

        i += 1 + length

    return None


def get_manufacturer_data(adv_data):
    adv_data = bytes(adv_data)
    i = 0
    while i + 1 < len(adv_data):
        length = adv_data[i]
        if length == 0:
            break

        adv_type = adv_data[i + 1]
        if adv_type == 0xFF:
            return bytes(adv_data[i + 2:i + 1 + length])

        i += 1 + length

    return None


def decode_sensor_payload(mfg):
    if not mfg or len(mfg) < 4:
        return None

    try:
        company_id, sensor_type, node_id = struct.unpack("<HBB", mfg[:4])

        if sensor_type == SENSOR_TYPE_DHT22:
            if len(mfg) < 8:
                return {
                    "company_id": company_id,
                    "sensor_type": sensor_type,
                    "node_id": node_id,
                    "error": "DHT22 payload too short"
                }

            company_id, sensor_type, node_id, temp_i, hum_i = struct.unpack("<HBBhh", mfg[:8])

            return {
                "company_id": company_id,
                "sensor_type": sensor_type,
                "sensor_name": "DHT22",
                "node_id": node_id,
                "temperature_c": temp_i / 100,
                "humidity_pct": hum_i / 100,
            }

        elif sensor_type == SENSOR_TYPE_BMP280:
            if len(mfg) < 10:
                return {
                    "company_id": company_id,
                    "sensor_type": sensor_type,
                    "node_id": node_id,
                    "error": "BMP280 payload too short"
                }

            company_id, sensor_type, node_id, temp_i, pressure_i = struct.unpack("<HBBhi", mfg[:10])

            return {
                "company_id": company_id,
                "sensor_type": sensor_type,
                "sensor_name": "BMP280",
                "node_id": node_id,
                "temperature_c": temp_i / 100,
                "pressure_hpa": pressure_i / 100,
            }

        else:
            return {
                "company_id": company_id,
                "sensor_type": sensor_type,
                "node_id": node_id,
                "error": "Unknown sensor type"
            }

    except Exception as e:
        return {
            "error": "Decode failed: {}".format(e)
        }


def bt_irq(event, data):
    if event == _IRQ_SCAN_RESULT:
        addr_type, addr, adv_type, rssi, adv_data = data

        addr_b = bytes(addr)
        adv_b = bytes(adv_data)

        name = decode_name(adv_b)

        if not name or not name.startswith(NAME_PREFIX):
            return

        mac = format_mac(addr_b)
        mfg = get_manufacturer_data(adv_b)
        decoded = decode_sensor_payload(mfg) if mfg else None

        seen[mac] = {
            "name": name,
            "rssi": rssi,
            "adv_type": adv_type,
            "mfg": mfg,
            "raw": adv_b,
            "decoded": decoded,
        }

    elif event == _IRQ_SCAN_DONE:
        print()
        print("=" * 60)
        print("Scan complete. ESP32C3 devices seen:", len(seen))
        print("=" * 60)

        for mac in sorted(seen.keys()):
            info = seen[mac]

            print("MAC: ", mac)
            print("Name:", info["name"])
            print("RSSI:", info["rssi"], "dBm")
            print("Adv type:", info["adv_type"])

            if info["mfg"]:
                print("Manufacturer data:", binascii.hexlify(info["mfg"]).decode())
            else:
                print("Manufacturer data: <none>")

            if info["decoded"]:
                decoded = info["decoded"]

                if "error" in decoded:
                    print("Decoded payload error:", decoded["error"])
                    if "company_id" in decoded:
                        print("  Company ID:", hex(decoded["company_id"]))
                    if "sensor_type" in decoded:
                        print("  Sensor type:", decoded["sensor_type"])
                    if "node_id" in decoded:
                        print("  Node ID:", decoded["node_id"])
                else:
                    print("Decoded payload:")
                    print("  Company ID:", hex(decoded["company_id"]))
                    print("  Sensor:", decoded["sensor_name"])
                    print("  Node ID:", decoded["node_id"])
                    print("  Temperature:", decoded["temperature_c"], "C")

                    if decoded["sensor_type"] == SENSOR_TYPE_DHT22:
                        print("  Humidity:", decoded["humidity_pct"], "%")
                    elif decoded["sensor_type"] == SENSOR_TYPE_BMP280:
                        print("  Pressure:", decoded["pressure_hpa"], "hPa")
            else:
                print("Decoded payload: <none>")

            print("Raw adv:", binascii.hexlify(info["raw"]).decode())
            print("-" * 60)

        print()


ble.irq(bt_irq)

print("Starting filtered BLE scanner: NAME_PREFIX = {}".format(NAME_PREFIX))

while True:
    seen.clear()
    print("Scanning for 5 seconds...")
    ble.gap_scan(5000, 30000, 30000)
    time.sleep(6)