# Import required modules
from machine import Pin
import time
import dht

# GPIO where the DHT22 DATA pin is connected
DHT_PIN = 21

# Create DHT22 sensor object
# Pin is set as input with internal pull-up enabled
sensor = dht.DHT22(Pin(DHT_PIN, Pin.IN, Pin.PULL_UP))

while True:
    try:
        # Trigger a new measurement
        sensor.measure()

        # Read temperature (Celsius) and humidity (%)
        temperature = sensor.temperature()
        humidity = sensor.humidity()

        # Print formatted output to Thonny shell
        print("Temperature: {:.1f} C | Humidity: {:.1f} %".format(temperature, humidity))

    except OSError as error:
        # Catch communication errors (timing issues, wiring problems, etc.)
        print("Sensor read error:", error)

    # DHT22 needs ~2 seconds between readings
    time.sleep(2)