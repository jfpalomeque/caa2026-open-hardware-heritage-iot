# ESP32-C3 + DHT22 (GPIO21) + WiFi AP + minimal web server

import network
import socket
import time

from machine import Pin
import dht

# -----------------------------
# Config
# -----------------------------
AP_SSID = "ESP32_DHT22_AP"
AP_PASSWORD = "12345678"  # 8+ chars required for WPA2
DHT_PIN = 21
AP_TXPOWER = 5              # workaround for this board

# -----------------------------
# Sensor setup
# -----------------------------
sensor = dht.DHT22(Pin(DHT_PIN))

def read_dht():
    """
    Returns (temp_c, humidity) or (None, None) if read fails.
    DHT sensors can be finicky; retry a couple of times.
    """
    for _ in range(3):
        try:
            sensor.measure()
            return sensor.temperature(), sensor.humidity()
        except Exception:
            time.sleep_ms(250)
    return None, None

# -----------------------------
# WiFi AP setup
# -----------------------------
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=AP_SSID, password=AP_PASSWORD, authmode=network.AUTH_WPA_WPA2_PSK, txpower=AP_TXPOWER)



ip = ap.ifconfig()[0]
print("AP active")
print("SSID:", AP_SSID)
print("Password:", AP_PASSWORD)
print("Open in browser: http://{}/".format(ip))

# -----------------------------
# Minimal HTTP server
# -----------------------------
def http_response(body, content_type="text/html; charset=utf-8", status="200 OK"):
    headers = [
        "HTTP/1.1 {}".format(status),
        "Content-Type: {}".format(content_type),
        "Connection: close",
        "Cache-Control: no-store",
        "",
        ""
    ]
    return "\r\n".join(headers) + body

def page_html(ip_addr, t, h):
    if t is None or h is None:
        reading = "<p><b>Sensor:</b> read failed (try refreshing)</p>"
        t_str, h_str = "N/A", "N/A"
    else:
        reading = "<p><b>Temperature:</b> {:.1f} C<br><b>Humidity:</b> {:.1f} %</p>".format(t, h)
        t_str, h_str = "{:.1f}".format(t), "{:.1f}".format(h)

    # Simple auto-refresh page (no fancy JS needed)
    return """<!doctype html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="3">
  <title>ESP32-C3 DHT22 Demo</title>
  <style>
    body {{ font-family: Arial; margin: 18px; }}
    .card {{ padding: 14px; border: 1px solid #ddd; border-radius: 10px; max-width: 420px; }}
    code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 6px; }}
  </style>
</head>
<body>
  <div class="card">
    <h2>ESP32-C3 WiFi AP + DHT22</h2>
    <p><b>AP IP:</b> {ip}</p>
    {reading}
    <p>JSON endpoint: <code>/json</code></p>
    <p>Auto-refresh every 3 seconds.</p>
    <p style="font-size: 12px; color: #666;">Last values: T={t}C, H={h}%</p>
  </div>
</body>
</html>
""".format(ip=ip_addr, reading=reading, t=t_str, h=h_str)

def json_body(t, h):
    if t is None or h is None:
        return '{{"ok":false,"error":"dht_read_failed"}}'
    return '{{"ok":true,"temperature_c":{:.1f},"humidity":{:.1f}}}'.format(t, h)

# Create listening socket
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(2)
print("Web server listening on", addr)

while True:
    try:
        cl, remote = s.accept()
        cl.settimeout(2)
        req = cl.recv(1024)
        if not req:
            cl.close()
            continue

        # Parse first line: GET /path HTTP/1.1
        try:
            line0 = req.split(b"\r\n", 1)[0]
            parts = line0.split()
            path = parts[1].decode() if len(parts) > 1 else "/"
        except Exception:
            path = "/"

        t, h = read_dht()

        if path == "/json":
            body = json_body(t, h)
            resp = http_response(body, content_type="application/json; charset=utf-8")
        else:
            body = page_html(ip, t, h)
            resp = http_response(body)

        cl.send(resp)
        cl.close()

    except Exception as e:
        # Keep the server alive even if a client disconnects weirdly
        print("Server error:", repr(e))
        try:
            cl.close()
        except Exception:
            pass
        time.sleep_ms(100)