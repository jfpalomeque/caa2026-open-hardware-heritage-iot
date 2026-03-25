'''
WiFi connection tester for the ESP32-C3. Connects to a WiFi network and
makes a simple HTTP request to example.com to confirm that the board has
internet access. Update SSID and PASSWORD with your network credentials.
'''
import network
import time
import socket

SSID = "YOUR_WIFI"
PASSWORD = "YOUR_PASS"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    time.sleep(1)
    wlan.active(True)

    print("Connecting...")
    wlan.connect(SSID, PASSWORD)

    timeout = 10
    while timeout > 0:
        if wlan.isconnected():
            break
        time.sleep(1)
        timeout -= 1

    if not wlan.isconnected():
        print("Failed to connect")
        return None

    print("Connected:", wlan.ifconfig())
    return wlan


def http_test():
    try:
        addr = socket.getaddrinfo("example.com", 80)[0][-1]
        s = socket.socket()
        s.settimeout(5)
        s.connect(addr)

        request = b"GET / HTTP/1.0\r\nHost: example.com\r\n\r\n"
        s.send(request)

        data = s.recv(100)
        s.close()

        print("HTTP OK")
        return True

    except Exception as e:
        print("HTTP failed:", e)
        return False


# ---- MAIN ----
wlan = connect_wifi()

if wlan:
    http_test()