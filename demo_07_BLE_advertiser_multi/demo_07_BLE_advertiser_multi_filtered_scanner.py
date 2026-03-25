'''
This is a simple BLE scanner that filters for devices with a name starting with "ESP32C3". 
It uses the Bluetooth Low Energy (BLE) functionality of the ESP32-C3 to scan for nearby devices and collects 
information about those that match the specified name prefix. The collected information includes the device's MAC 
address, name, RSSI (signal strength), advertising type, manufacturer data, and raw advertising data. The results are printed to 
the console after each scan cycle.

'''
import bluetooth
import binascii
import time

ble = bluetooth.BLE()
ble.active(True)

_IRQ_SCAN_RESULT = 5
_IRQ_SCAN_DONE = 6

seen = {}

NAME_PREFIX = "ESP32C3"

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


def bt_irq(event, data):
    if event == _IRQ_SCAN_RESULT:
        addr_type, addr, adv_type, rssi, adv_data = data

        addr_b = bytes(addr)
        adv_b = bytes(adv_data)

        name = decode_name(adv_b)

        
        if not name or not name.startswith(NAME_PREFIX): #filter
            return

        mac = format_mac(addr_b)
        mfg = get_manufacturer_data(adv_b)

        seen[mac] = {
            "name": name,
            "rssi": rssi,
            "adv_type": adv_type,
            "mfg": mfg,
            "raw": adv_b,
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

            print("Raw adv:", binascii.hexlify(info["raw"]).decode())
            print("-" * 60)

        print()


ble.irq(bt_irq)

print(f"Starting filtered BLE scanner:  NAME_PREFIX = {NAME_PREFIX}")

while True:
    seen.clear()
    print("Scanning for 5 seconds...")
    ble.gap_scan(5000, 30000, 30000)
    time.sleep(6)