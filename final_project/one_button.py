import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while(True):
    time.sleep(0.2)
    if(GPIO.input(17) == False):
        print(" ")
        print("Button 17 was pressed")
