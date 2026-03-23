import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

print("MAC:", wlan.config('mac'))
print("MAC hex:", ':'.join('{:02X}'.format(b) for b in wlan.config('mac')))