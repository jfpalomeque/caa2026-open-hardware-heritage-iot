import bluetooth
import struct
import time
from machine import Pin
import dht

# =========================
# Config
# =========================
DEVICE_NAME = "ESP32C3_DHT_NOTIFY"
DHT_PIN = 21

# Custom UUIDs
ENV_SVC_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
DATA_CHAR_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef3")

# =========================
# BLE setup
# =========================
ble = bluetooth.BLE()
ble.active(True)

# Characteristic with READ + NOTIFY
DATA_CHAR = (DATA_CHAR_UUID, bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY)
ENV_SERVICE = (ENV_SVC_UUID, (DATA_CHAR,))

((data_handle,),) = ble.gatts_register_services((ENV_SERVICE,))

# =========================
# Sensor setup
# =========================
sensor = dht.DHT22(Pin(DHT_PIN))

# =========================
# BLE connection tracking
# =========================
_IRQ_CENTRAL_CONNECT = 1
_IRQ_CENTRAL_DISCONNECT = 2

connections = set()

def advertising_payload(name=None):
    payload = bytearray()

    def _append(adv_type, value):
        payload.extend(struct.pack("BB", len(value) + 1, adv_type))
        payload.extend(value)

    if name:
        _append(0x09, name.encode())  # Complete Local Name

    return payload

payload = advertising_payload(name=DEVICE_NAME)

def bt_irq(event, data):
    if event == _IRQ_CENTRAL_CONNECT:
        conn_handle, addr_type, addr = data
        connections.add(conn_handle)
        print("Central connected:", conn_handle)

    elif event == _IRQ_CENTRAL_DISCONNECT:
        conn_handle, addr_type, addr = data
        if conn_handle in connections:
            connections.remove(conn_handle)
        print("Central disconnected:", conn_handle)
        ble.gap_advertise(100_000, adv_data=payload)

ble.irq(bt_irq)

def read_dht():
    for _ in range(3):
        try:
            sensor.measure()
            temp = sensor.temperature()
            hum = sensor.humidity()
            return temp, hum
        except Exception:
            time.sleep_ms(250)
    return None, None

# Start advertising
ble.gap_advertise(100_000, adv_data=payload)

print("DHT22 notify peripheral started")
print("Advertising as:", DEVICE_NAME)

# =========================
# Main loop
# =========================
while True:
    temp, hum = read_dht()

    if temp is None or hum is None:
        print("DHT22 read failed")
        time.sleep(2)
        continue

    packed = struct.pack("<ff", temp, hum)

    # Update characteristic value
    ble.gatts_write(data_handle, packed)

    # Notify all connected centrals
    for conn_handle in list(connections):
        try:
            ble.gatts_notify(conn_handle, data_handle, packed)
        except Exception as e:
            print("Notify error:", e)

    print("Sent notification")
    print("  Temp:", temp, "C")
    print("  Hum :", hum, "%")
    print("  Connected centrals:", len(connections))
    print()

    time.sleep(2)