import RPi.GPIO as GPIO
from time import sleep



clk1 = 13
dt1 = 6

clk0 = 21
dt0 = 20

count0 = 0
count1 = 0

def click0_cb(NULL):
    global count0
    dir = GPIO.input(20)
    

    if(dir):
        count0+=1
    else:
        count0-=1
    print(f"click 0: {count0}")


def click1_cb(NULL):
    global count1
    dir = GPIO.input(6)

    if(dir):
        count1+=1
    else:
        count1-=1
    print(f"click 1: {count1}")

GPIO.setmode(GPIO.BCM)
GPIO.setup(clk0, GPIO.IN)
GPIO.setup(dt0, GPIO.IN)
GPIO.setup(clk1, GPIO.IN)
GPIO.setup(dt1, GPIO.IN  )

GPIO.add_event_detect(clk0, GPIO.RISING, callback=click0_cb, bouncetime=100)

GPIO.add_event_detect(clk1, GPIO.RISING, callback=click1_cb, bouncetime=100)



try:

        while True:
                sleep(0.01)
finally:
        GPIO.cleanup()