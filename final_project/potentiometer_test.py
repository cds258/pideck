#!/usr/bin/env python3
import serial


def map_value(x, original_max=29.35, target_max=1):
    return x / original_max

# Example Usage:
mapped_value = map_value(15)  # Map 15 from [0, 29.35] to [0, 1]
print("Mapped Value:", mapped_value)

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.reset_input_buffer()


    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').rstrip()
            # Initialize an empty dictionary to store the values
            data = {}
            if line:
                try:
                    # Split the line by commas and filter out empty strings
                    entries = filter(None, line.split(','))
                    # Loop through each non-empty entry and parse it
                    for entry in entries:
                        # Split the entry into key and value parts
                        key, value = entry.split(':')
                        # Clean up any whitespace and convert value to float
                        key = key.strip()
                        value = float(value.strip())
                        data[key] = map_value(value)
                    # Now you can use the data dictionary for further processing
                    print(data)  # Example usage
                except ValueError as e:
                    print(f"Error parsing line: {line}, Error: {e}")

def update_volumes():
   channels[0].set_volume(data['pot#l'])
   channels[1].set_volume(data['pot#r'])
