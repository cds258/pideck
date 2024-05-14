import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Define thresholds
# HIGH_THRESHOLD = 0.8  # Set a higher threshold for detecting high state
# LOW_THRESHOLD = 0.3   # Set a lower threshold for detecting low state

while(True):
    time.sleep(0.2)
    if(GPIO.input(26)):
        time.sleep(0.02)  # Debounce delay
        if( GPIO.input(26)):
            print(" ")
            print("Button Left Right was pressed")
    elif(GPIO.input(19)):
        time.sleep(0.02)  # Debounce delay
        if( GPIO.input(19)):
            print(" ")
            print("Button Left Left was pressed")
    elif(GPIO.input(12)):
        time.sleep(0.02)  # Debounce delay
        if( GPIO.input(12)):
            print(" ")
            print("Button Right Right was pressed")
    elif(GPIO.input(16)):
        time.sleep(0.02)  # Debounce delay
        if( GPIO.input(16)):
            print(" ")
            print("Button Right Left was pressed")
