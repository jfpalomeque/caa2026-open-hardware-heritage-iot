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

# RAM buffer to temporarily store ADC readings
# Buffering reduces how often we write to flash, extending flash lifetime
buffer = []

# Open (or create) a CSV file in append mode
# Append mode ensures existing data is preserved
with open("ldr.csv", "a") as f:
    # Infinite loop: log data until the board is reset or powered off
    while True:
        # Read the current light level from the ADC
        value = adc.read()

        # Convert the value to a string and store it in RAM
        buffer.append(str(value))

        # Once we have collected 10 readings,
        # write them to flash in a single operation
        if len(buffer) >= 10:
            # Join all buffered values with newlines
            # This creates a block of text to write at once
            f.write("\n".join(buffer) + "\n")

            # Force the data to be written to flash immediately
            f.flush()

            # Clear the buffer so we can start collecting again
            buffer.clear()

        # Wait 1 second before taking the next reading
        # This sets the sampling rate to 1 Hz
        time.sleep(1)
