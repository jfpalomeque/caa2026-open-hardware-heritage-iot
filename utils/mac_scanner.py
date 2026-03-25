'''
Prints the MAC address of the ESP32-C3 WiFi interface. Useful for
identifying boards when setting up ESP-NOW or other peer-to-peer
communication that requires knowing the MAC address of each device.
'''
import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

print("MAC:", wlan.config('mac'))
print("MAC hex:", ':'.join('{:02X}'.format(b) for b in wlan.config('mac')))