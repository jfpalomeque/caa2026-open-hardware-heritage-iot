import bluetooth
import time

ble = bluetooth.BLE()
ble.active(True)

TARGET_NAME = "ESP32C3_advertiser"

_IRQ_SCAN_RESULT = 5
_IRQ_SCAN_DONE = 6

def decode_name(adv_data):
    adv_data = bytes(adv_data)   # convert memoryview to bytes
    i = 0
    while i + 1 < len(adv_data):
        length = adv_data[i]
        if length == 0:
            break
        adv_type = adv_data[i + 1]
        if adv_type in (0x08, 0x09):  # Shortened or Complete Local Name
            return bytes(adv_data[i + 2:i + 1 + length]).decode("utf-8", "ignore")
        i += 1 + length
    return None

def bt_irq(event, data):
    if event == _IRQ_SCAN_RESULT:
        addr_type, addr, adv_type, rssi, adv_data = data
        name = decode_name(adv_data)
        if name == TARGET_NAME:
            mac = ":".join("{:02X}".format(b) for b in bytes(addr))
            print("Found:", name, "| MAC:", mac, "| RSSI:", rssi, "dBm")

    elif event == _IRQ_SCAN_DONE:
        print("Scan complete\n")

ble.irq(bt_irq)

while True:
    print("Scanning for 5 seconds...")
    ble.gap_scan(5000, 30000, 30000)
    time.sleep(6)