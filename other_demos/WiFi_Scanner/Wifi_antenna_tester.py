'''
WiFi scanner for the ESP32-C3. Scans for nearby WiFi networks and prints
the SSID and signal strength (RSSI) of up to 10 networks.
Useful for testing the antenna and checking WiFi reception.
'''
import network
import time

w = network.WLAN(network.STA_IF)
w.active(True)
time.sleep(2)

nets = w.scan()
print("Networks found:", len(nets))

for n in nets[:10]:
    ssid = n[0].decode() if isinstance(n[0], bytes) else n[0]
    print(ssid, n[3])