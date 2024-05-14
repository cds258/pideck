from RPi import GPIO
from time import sleep

clk1 = 13
dt1 = 6

clk0 = 21
dt0 = 20

count0 = 0
count1 = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(clk0, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt0, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(clk1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

clk0LastState = GPIO.input(clk0)
clk1LastState = GPIO.input(clk0)


def handle_rotary0():
        global count0, clk0LastState
        clk0State = GPIO.input(clk0)
        dt0State = GPIO.input(dt0)
        if clk0State != clk0LastState:
                if dt0State != clk0State:
                        count0 += 1
                else:
                        count0 -= 1
                print(f"count0: {count0}")
        clk0LastState = clk0State

def handle_rotary1():
        global count1, clk1LastState
        clk1State = GPIO.input(clk1)
        dt1State = GPIO.input(dt1)
        if clk1State != clk1LastState:
                if dt1State != clk1State:
                        count1 += 1
                else:
                        count1 -= 1
                print(f"count1: {count1}")
        clk1LastState = clk1State

try:

        while True:
             handle_rotary1()
             handle_rotary0()
             sleep(0.01)
finally:
        GPIO.cleanup()