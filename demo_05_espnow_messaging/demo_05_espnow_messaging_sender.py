'''
ESP-NOW Messaging Demo - Sender
This is the sender code for the ESP-NOW Messaging demo. It allows you to send messages to a receiver board using ESP-NOW.
Make sure to update the PEER_MAC variable with the MAC address of your receiver board, 
or use the broadcast MAC to send to all receivers on the same channel.
'''
import network
import espnow
import time

# --------------------------
# CONFIG
# --------------------------
CHANNEL = 1
PEER_MAC = b'\xff\xff\xff\xff\xff\xff' #<-- Broadcast MAC
#PEER_MAC = b'\x0cN\xa0c\xed\x84'   # <-- replace with Receiver Board MAC

# --------------------------
# Wi-Fi setup
# --------------------------
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

print("Sender ready")
print("My MAC:", ':'.join('{:02X}'.format(b) for b in wlan.config('mac')))
print("Sending to:", ':'.join('{:02X}'.format(b) for b in PEER_MAC))
print("Channel:", CHANNEL)

# --------------------------
# ESP-NOW setup
# --------------------------
e = espnow.ESPNow()
e.active(True)
e.add_peer(PEER_MAC)

# --------------------------
# Chat loop
# --------------------------
while True:
    msg = input("Type message: ").strip()
    if not msg:
        continue

    try:
        e.send(PEER_MAC, msg)
        print("Sent:", msg)
    except Exception as ex:
        print("Send failed:", ex)