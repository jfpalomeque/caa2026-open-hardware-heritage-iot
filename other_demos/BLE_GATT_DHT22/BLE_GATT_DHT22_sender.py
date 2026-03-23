import bluetooth
import struct
import time
from machine import Pin
import dht

# =========================
# Config
# =========================
DEVICE_NAME = "ESP32C3_DHT_GATT"
DHT_PIN = 21

# Custom UUIDs
ENV_SVC_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
TEMP_CHAR_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef1")
HUM_CHAR_UUID  = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef2")

# =========================
# BLE setup
# =========================
ble = bluetooth.BLE()
ble.active(True)

# Characteristic definitions
TEMP_CHAR = (TEMP_CHAR_UUID, bluetooth.FLAG_READ)
HUM_CHAR  = (HUM_CHAR_UUID, bluetooth.FLAG_READ)
ENV_SERVICE = (ENV_SVC_UUID, (TEMP_CHAR, HUM_CHAR))

# Register service
((temp_handle, hum_handle),) = ble.gatts_register_services((ENV_SERVICE,))

# =========================
# Sensor setup
# =========================
sensor = dht.DHT22(Pin(DHT_PIN))

# =========================
# Helpers
# =========================
def advertising_payload(name=None):
    payload = bytearray()

    def _append(adv_type, value):
        payload.extend(struct.pack("BB", len(value) + 1, adv_type))
        payload.extend(value)

    if name:
        _append(0x09, name.encode())  # Complete Local Name

    return payload


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


# =========================
# IRQ handler
# =========================
_IRQ_CENTRAL_CONNECT = 1
_IRQ_CENTRAL_DISCONNECT = 2

connections = set()

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

# Start advertising
payload = advertising_payload(name=DEVICE_NAME)
ble.gap_advertise(100_000, adv_data=payload)

print("DHT22 GATT peripheral started")
print("Advertising as:", DEVICE_NAME)

# =========================
# Main loop
# =========================
while True:
    temp, hum = read_dht()

    if temp is not None and hum is not None:
        # Store as little-endian floats
        ble.gatts_write(temp_handle, struct.pack("<f", temp))
        ble.gatts_write(hum_handle, struct.pack("<f", hum))

        print("Updated values")
        print("  Temperature:", temp, "C")
        print("  Humidity   :", hum, "%")
    else:
        print("DHT22 read failed")

    time.sleep(2)