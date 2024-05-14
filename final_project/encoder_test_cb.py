import RPi.GPIO as GPIO
from time import sleep

# Setup
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
pin_a = 20  # Encoder pin A
pin_b = 21  # Encoder pin B

GPIO.setup(pin_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pin_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)

counter = 0
last_state = None

# Callback function
def rotary_callback(channel):
    global counter, last_state
    state_a = GPIO.input(pin_a)
    state_b = GPIO.input(pin_b)
    if state_a and state_b:
        if last_state == "CW":
            counter += 1
            print("Counter: ", counter)
        elif last_state == "CCW":
            counter -= 1
            print("Counter: ", counter)
    elif state_a and not state_b:
        last_state = "CW"
    elif not state_a and state_b:
        last_state = "CCW"

# Add event detection
GPIO.add_event_detect(pin_a, GPIO.BOTH, callback=rotary_callback, bouncetime=2)
GPIO.add_event_detect(pin_b, GPIO.BOTH, callback=rotary_callback, bouncetime=2)

try:
    while True:
       sleep(0.01)
except KeyboardInterrupt:
    GPIO.cleanup()  # Clean up GPIO on CTRL+C exit
