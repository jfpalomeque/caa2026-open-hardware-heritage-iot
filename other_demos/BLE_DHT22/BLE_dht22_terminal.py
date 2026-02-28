import time
import struct
from machine import Pin
import dht
import ubluetooth

# DHT22
sensor = dht.DHT22(Pin(21))

_IRQ_CENTRAL_CONNECT = 1
_IRQ_CENTRAL_DISCONNECT = 2

# NUS UUIDs
_UART_SERVICE_UUID = ubluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_RX_UUID      = ubluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX_UUID      = ubluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")

_UART_RX = (_UART_RX_UUID, ubluetooth.FLAG_WRITE)
_UART_TX = (_UART_TX_UUID, ubluetooth.FLAG_NOTIFY)
_UART_SERVICE = (_UART_SERVICE_UUID, (_UART_TX, _UART_RX))

def _append(payload, ad_type, value: bytes):
    payload += struct.pack("BB", len(value) + 1, ad_type) + value
    return payload

def adv_payload(name: str):
    # Keep ADV small: Flags + Complete Local Name
    p = bytearray()
    p = _append(p, 0x01, b"\x06")              # Flags: LE General Disc + BR/EDR not supported
    p = _append(p, 0x09, name.encode())        # Complete local name
    return p

def resp_payload(uuid128: ubluetooth.UUID):
    # Put 128-bit UUID in scan response so ADV stays under 31 bytes
    p = bytearray()
    p = _append(p, 0x07, bytes(uuid128))       # Complete list of 128-bit Service UUIDs
    return p

class BLE_DHT22_NUS:
    def __init__(self, ble, name="C3DHT"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)

        ((self._tx_handle, self._rx_handle),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._connections = set()

        # IMPORTANT: short name in ADV so it fits
        self._adv = adv_payload(name)
        self._resp = resp_payload(_UART_SERVICE_UUID)

        self.advertise()

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
            print("BLE connected:", conn_handle)

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.discard(conn_handle)
            print("BLE disconnected:", conn_handle)
            self.advertise()

    def advertise(self, interval_us=250000):
        # Do not call gap_advertise(None) first; on some ports it can error
        self._ble.gap_advertise(interval_us, adv_data=self._adv, resp_data=self._resp)
        print("Advertising (name in ADV, UUID in scan response)")

    def notify_text(self, text: str):
        if not self._connections:
            return
        data = text.encode()
        for conn_handle in tuple(self._connections):
            try:
                self._ble.gatts_notify(conn_handle, self._tx_handle, data)
            except Exception as e:
                self._connections.discard(conn_handle)
                print("Notify failed:", e)

ble = ubluetooth.BLE()
nus = BLE_DHT22_NUS(ble, name="C3DHT")

while True:
    try:
        sensor.measure()
        t = sensor.temperature()
        h = sensor.humidity()
        msg = "T={:.1f}C H={:.1f}%".format(t, h)
    except Exception as e:
        msg = "DHT error"
        print("Sensor error:", e)

    print(msg)
    nus.notify_text(msg + "\n")
    time.sleep(1)