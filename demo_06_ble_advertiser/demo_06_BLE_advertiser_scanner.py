'''
This example demonstrates how to create a BLE scanner using the ESP32-C3's Bluetooth Low Energy 
(BLE) capabilities. The device will scan for nearby BLE advertisers and print out the name, MAC 
address, and RSSI of any devices it finds that match a specified target name.

To run this example, you will need to have the ESP32-C3 set up with MicroPython and the necessary Bluetooth 
libraries. The code initializes the BLE module, sets up an interrupt handler to process scan results, and starts 
scanning for nearby BLE devices. When a device with the target name is found, its details are printed to the console.

You can use a BLE advertiser (like the one in demo_06_BLE_advertiser.py) to broadcast a device name that this scanner 
will look for. When the advertiser is running, you should see its details printed by the scanner when it is discovered.
'''
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