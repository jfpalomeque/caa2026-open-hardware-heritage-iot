import network
import espnow
import time

# --------------------------
# Wi-Fi setup
# --------------------------
CHANNEL = 1

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
try:
    wlan.disconnect()
except:
    pass

try:
    wlan.config(channel=CHANNEL)
except:
    pass

print("Receiver ready")
print("My MAC:", ':'.join('{:02X}'.format(b) for b in wlan.config('mac')))
print("Listening on channel", CHANNEL)

# --------------------------
# ESP-NOW setup
# --------------------------
e = espnow.ESPNow()
e.active(True)

# --------------------------
# Main loop
# --------------------------
while True:
    host, msg = e.recv()
    if msg:
        try:
            text = msg.decode()
        except:
            text = str(msg)

        mac_str = ':'.join('{:02X}'.format(b) for b in host)
        print("[FROM {}] {}".format(mac_str, text))