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