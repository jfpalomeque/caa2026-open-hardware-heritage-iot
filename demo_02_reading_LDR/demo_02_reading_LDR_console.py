from machine import ADC, Pin
import time

# Create an ADC object on GPIO0
# This pin is connected to the middle of the LDR voltage divider
adc = ADC(Pin(0))

# Set ADC attenuation to 11 dB
# This allows the ADC to measure voltages up to about 3.3 V,
# as the max voltage and ADC pin can read is around 1.1v
adc.atten(ADC.ATTN_11DB)

# Set ADC resolution to 12 bits
# The ADC will return values from 0 to 4095
adc.width(ADC.WIDTH_12BIT)

# Infinite loop to continuously read the light level
while True:
    # Read the current analog value from the ADC
    # Higher value = more light, lower value = less light
    value = adc.read()
    
    # Print the ADC value to the Thonny console
    print(value)
    
    # Wait half a second before taking the next reading
    time.sleep(0.5)