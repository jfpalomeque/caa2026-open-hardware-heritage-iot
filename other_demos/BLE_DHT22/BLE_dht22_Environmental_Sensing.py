import time
import struct
from machine import Pin
import dht
import ubluetooth

# DHT22
sensor = dht.DHT22(Pin(21))

# BLE IRQ events
_IRQ_CENTRAL_CONNECT = 1
_IRQ_CENTRAL_DISCONNECT = 2

# Standard Environmental Sensing Service and characteristics
_ENV_SVC = ubluetooth.UUID(0x181A)
_TEMP_CHR = ubluetooth.UUID(0x2A6E)  # Temperature, sint16, 0.01 C
_HUM_CHR  = ubluetooth.UUID(0x2A6F)  # Humidity, uint16, 0.01 %

# Flags
# Read lets phone read the value
# Notify lets phone subscribe and receive updates automatically
_TEMP = (_TEMP_CHR, ubluetooth.FLAG_READ | ubluetooth.FLAG_NOTIFY)
_HUM  = (_HUM_CHR,  ubluetooth.FLAG_READ | ubluetooth.FLAG_NOTIFY)
_ENV_SERVICE = (_ENV_SVC, (_TEMP, _HUM))

def _adv_payload(name: str, services):
    # Keep advertising small to avoid OSError -18
    payload = bytearray()

    def _append(ad_type, value: bytes):
        payload.extend(struct.pack("BB", len(value) + 1, ad_type))
        payload.extend(value)

    _append(0x01, b"\x06")                 # Flags
    _append(0x09, name.encode())           # Complete local name

    # Add 16-bit service UUIDs (Environmental Sensing is 16-bit)
    for svc in services:
        b = bytes(svc)
        if len(b) == 2:
            _append(0x03, b)               # Complete list of 16-bit UUIDs

    return payload

class BLEEnv:
    def __init__(self, name="C3-ENV"):
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self._irq)

        ((self.h_temp, self.h_hum),) = self.ble.gatts_register_services((_ENV_SERVICE,))
        self.connections = set()

        self.adv_data = _adv_payload(name, services=[_ENV_SVC])
        self.advertise()

        # Initialize characteristic values
        self.set_values(0.0, 0.0)

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self.connections.add(conn_handle)
            print("Connected:", conn_handle)

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self.connections.discard(conn_handle)
            print("Disconnected:", conn_handle)
            self.advertise()

    def advertise(self, interval_us=250000):
        self.ble.gap_advertise(interval_us, adv_data=self.adv_data)
        print("Advertising Environmental Sensing as BLE device")

    def set_values(self, temp_c: float, hum_pc: float):
        temp_x100 = int(temp_c * 100)
        hum_x100 = int(hum_pc * 100)

        # Write to GATT database
        self.ble.gatts_write(self.h_temp, struct.pack("<h", temp_x100))
        self.ble.gatts_write(self.h_hum,  struct.pack("<H", hum_x100))

        # Notify subscribers
        if self.connections:
            t_bytes = struct.pack("<h", temp_x100)
            h_bytes = struct.pack("<H", hum_x100)
            for ch in tuple(self.connections):
                try:
                    self.ble.gatts_notify(ch, self.h_temp, t_bytes)
                    self.ble.gatts_notify(ch, self.h_hum,  h_bytes)
                except Exception as e:
                    self.connections.discard(ch)
                    print("Notify failed:", e)

env = BLEEnv(name="C3-ENV")

last_good = (0.0, 0.0)

while True:
    try:
        sensor.measure()
        t = sensor.temperature()
        h = sensor.humidity()
        last_good = (t, h)
    except Exception as e:
        print("DHT read error:", e)
        t, h = last_good

    env.set_values(t, h)
    print("T={:.1f}C H={:.1f}%".format(t, h))

    # DHT22: keep reads about every 2 seconds or slower
    time.sleep(2)