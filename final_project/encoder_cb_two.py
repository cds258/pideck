import RPi.GPIO as GPIO

# Setup
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
# Encoder 1
pin_a1 = 20  # Encoder 1 pin A
pin_b1 = 21  # Encoder 1 pin B
# Encoder 2
pin_a2 = 13  # Encoder 2 pin A
pin_b2 = 6  # Encoder 2 pin B

GPIO.setup([pin_a1, pin_b1, pin_a2, pin_b2], GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Counters for each encoder
counter1 = 0
last_state1 = None
counter2 = 0
last_state2 = None

# Callback function for Encoder 1
def rotary_callback1(channel):
    global counter1, last_state1
    state_a = GPIO.input(pin_a1)
    state_b = GPIO.input(pin_b1)
    if state_a and state_b:
        if last_state1 == "CW":
            counter1 += 1
        elif last_state1 == "CCW":
            counter1 -= 1
        print("Encoder 1 Counter: ", counter1)
    elif state_a and not state_b:
        last_state1 = "CW"
    elif not state_a and state_b:
        last_state1 = "CCW"

# Callback function for Encoder 2
def rotary_callback2(channel):
    global counter2, last_state2
    state_a = GPIO.input(pin_a2)
    state_b = GPIO.input(pin_b2)
    if state_a and state_b:
        if last_state2 == "CW":
            counter2 += 1
        elif last_state2 == "CCW":
            counter2 -= 1
        print("Encoder 2 Counter: ", counter2)
    elif state_a and not state_b:
        last_state2 = "CW"
    elif not state_a and state_b:
        last_state2 = "CCW"

# Add event detection for both encoders
GPIO.add_event_detect(pin_a1, GPIO.BOTH, callback=rotary_callback1, bouncetime=2)
GPIO.add_event_detect(pin_b1, GPIO.BOTH, callback=rotary_callback1, bouncetime=2)
GPIO.add_event_detect(pin_a2, GPIO.BOTH, callback=rotary_callback2, bouncetime=2)
GPIO.add_event_detect(pin_b2, GPIO.BOTH, callback=rotary_callback2, bouncetime=2)

try:
    while True:
        pass  # Loop indefinitely
except KeyboardInterrupt:
    GPIO.cleanup()  # Clean up GPIO on CTRL+C exit
