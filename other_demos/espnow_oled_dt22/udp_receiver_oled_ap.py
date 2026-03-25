'''
ESP-NOW receiver that displays incoming DHT22 sensor data on a TTGO T-Display
(ESP32 with ST7789 TFT screen). Shows the sender MAC address, temperature,
humidity, and message count. If no data arrives for 8 seconds, shows a timeout
message. This script runs on the TTGO T-Display, not the ESP32-C3 SuperMini.
'''
# Working on a TTGO T-Display(ESP32)
from machine import Pin, SPI
import network
import espnow
import time
import st7789

# ==== DISPLAY CONFIG (your working settings) ====
SCK = 18
MOSI = 19
CS = 5
DC = 16
RST = 23
BL = 4

WIDTH = 135
HEIGHT = 240

# ==== INIT DISPLAY ====
def init_display():
    Pin(BL, Pin.OUT).on()

    spi = SPI(
        2,
        baudrate=20_000_000,
        polarity=1,
        phase=1,
        sck=Pin(SCK),
        mosi=Pin(MOSI),
        miso=Pin(0)
    )

    tft = st7789.ST7789(
        spi,
        WIDTH,
        HEIGHT,
        reset=Pin(RST, Pin.OUT),
        cs=Pin(CS, Pin.OUT),
        dc=Pin(DC, Pin.OUT),
        rotation=0,
        invert=True
    )

    tft.init()
    tft.fill(0)
    tft.show()
    return tft

def show_lines(tft, lines):
    tft.fill(0)
    y = 5
    for line in lines:
        tft.text(line, 5, y, 0xFFFF, 0)
        y += 14
    tft.show()

# ==== WIFI + ESPNOW ====
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()

rx_mac = sta.config("mac")
print("Receiver MAC:", rx_mac)

tft = init_display()

mac_str = ":".join("{:02x}".format(b) for b in rx_mac)

show_lines(tft, [
    "ESP-NOW Receiver",
    "MAC:",
    mac_str,
    "Waiting..."
])

e = espnow.ESPNow()
e.active(True)

last = time.ticks_ms()

while True:
    host, msg = e.recv(300)

    if msg:
        try:
            s = msg.decode()
            parts = s.split(",")

            temp = float(parts[0])
            hum = float(parts[1])
            count = int(parts[2])

            sender_mac = ":".join("{:02x}".format(b) for b in host)

            show_lines(tft, [
                "ESP-NOW Receiver",
                "From:",
                sender_mac,
                "Temp: {:.1f} C".format(temp),
                "Hum : {:.1f} %".format(hum),
                "N   : {}".format(count),
            ])

            print("Received:", s)
            last = time.ticks_ms()

        except Exception as ex:
            print("Parse error:", ex)

    if time.ticks_diff(time.ticks_ms(), last) > 8000:
        show_lines(tft, [
            "ESP-NOW Receiver",
            "No data (8s)"
        ])
        last = time.ticks_ms()
