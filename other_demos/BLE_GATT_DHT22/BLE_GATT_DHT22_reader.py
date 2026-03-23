import bluetooth
import struct
import time

# =========================
# Config
# =========================
TARGET_NAME = "ESP32C3_DHT_GATT"

ENV_SVC_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
TEMP_CHAR_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef1")
HUM_CHAR_UUID  = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef2")

# =========================
# BLE setup
# =========================
ble = bluetooth.BLE()
ble.active(True)

# IRQ constants
_IRQ_SCAN_RESULT = 5
_IRQ_SCAN_DONE = 6
_IRQ_PERIPHERAL_CONNECT = 7
_IRQ_PERIPHERAL_DISCONNECT = 8
_IRQ_GATTC_SERVICE_RESULT = 9
_IRQ_GATTC_SERVICE_DONE = 10
_IRQ_GATTC_CHARACTERISTIC_RESULT = 11
_IRQ_GATTC_CHARACTERISTIC_DONE = 12
_IRQ_GATTC_READ_RESULT = 15
_IRQ_GATTC_READ_DONE = 16

# State
conn_handle = None
target_addr_type = None
target_addr = None

start_handle = None
end_handle = None

temp_value_handle = None
hum_value_handle = None

read_stage = 0  # 0 = read temp next, 1 = read hum next

# =========================
# Helpers
# =========================
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


def format_mac(addr):
    return ":".join("{:02X}".format(b) for b in bytes(addr))


def start_scan():
    global target_addr_type, target_addr
    target_addr_type = None
    target_addr = None
    print("Scanning...")
    try:
        ble.gap_scan(5000, 30000, 30000)
    except OSError as e:
        print("Scan error:", e)


# =========================
# IRQ handler
# =========================
def bt_irq(event, data):
    global conn_handle, target_addr_type, target_addr
    global start_handle, end_handle
    global temp_value_handle, hum_value_handle
    global read_stage

    if event == _IRQ_SCAN_RESULT:
        addr_type, addr, adv_type, rssi, adv_data = data
        name = decode_name(adv_data)

        if name == TARGET_NAME:
            target_addr_type = addr_type
            target_addr = bytes(addr)
            print("Found target:", name)
            print("MAC:", format_mac(target_addr), "| RSSI:", rssi)
            ble.gap_scan(None)

    elif event == _IRQ_SCAN_DONE:
        if target_addr is not None:
            print("Connecting...")
            try:
                ble.gap_connect(target_addr_type, target_addr)
            except OSError as e:
                print("Connect error:", e)
        else:
            print("Target not found, rescanning soon")

    elif event == _IRQ_PERIPHERAL_CONNECT:
        conn_handle_, addr_type, addr = data
        conn_handle = conn_handle_
        print("Connected to peripheral")
        ble.gattc_discover_services(conn_handle)

    elif event == _IRQ_PERIPHERAL_DISCONNECT:
        print("Disconnected")
        conn_handle = None
        start_handle = None
        end_handle = None
        temp_value_handle = None
        hum_value_handle = None
        read_stage = 0

    elif event == _IRQ_GATTC_SERVICE_RESULT:
        conn_handle_, start, end, uuid = data
        if uuid == ENV_SVC_UUID:
            start_handle = start
            end_handle = end
            print("Service found:", start_handle, end_handle)

    elif event == _IRQ_GATTC_SERVICE_DONE:
        if start_handle is not None and end_handle is not None:
            print("Discovering characteristics...")
            ble.gattc_discover_characteristics(conn_handle, start_handle, end_handle)
        else:
            print("Service not found")

    elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
        conn_handle_, def_handle, value_handle, properties, uuid = data

        if uuid == TEMP_CHAR_UUID:
            temp_value_handle = value_handle
            print("Temperature characteristic handle:", temp_value_handle)

        elif uuid == HUM_CHAR_UUID:
            hum_value_handle = value_handle
            print("Humidity characteristic handle:", hum_value_handle)

    elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
        if temp_value_handle is not None:
            read_stage = 0
            ble.gattc_read(conn_handle, temp_value_handle)
        else:
            print("Temperature characteristic not found")

    elif event == _IRQ_GATTC_READ_RESULT:
        conn_handle_, value_handle, char_data = data

        if value_handle == temp_value_handle:
            temp = struct.unpack("<f", char_data)[0]
            print("Temperature:", round(temp, 2), "C")

        elif value_handle == hum_value_handle:
            hum = struct.unpack("<f", char_data)[0]
            print("Humidity   :", round(hum, 2), "%")

    elif event == _IRQ_GATTC_READ_DONE:
        if read_stage == 0 and hum_value_handle is not None:
            read_stage = 1
            ble.gattc_read(conn_handle, hum_value_handle)
        else:
            print("Read complete\n")


ble.irq(bt_irq)

print("BLE central reader started")
start_scan()

# =========================
# Main loop
# =========================
while True:
    time.sleep(1)