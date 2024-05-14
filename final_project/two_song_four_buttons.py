import pygame
import time
import RPi.GPIO as GPIO
# Initialize Pygame
pygame.init()

# Initiliaze GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27,GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize the mixer
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)

# Load two MP3 tracks
track1 = pygame.mixer.Sound('Music.wav')
track2 = pygame.mixer.Sound('Yup_I_Guess.wav')

# Create separate channels for each track
channel1 = pygame.mixer.Channel(0)
channel2 = pygame.mixer.Channel(1)

started = False
waiting = True
while waiting:
    if (not GPIO.input(17)):
        started = True
        waiting = False
# Play both tracks
while started:
    playing = True
    channel1.play(track1)
    channel2.play(track2)
    while playing:
        # Set volume variables
        c1v = 0.5
        c2v = 0.5
        # Set volume (0.0 to 1.0)
        channel1.set_volume(c1v)  # Half volume for track 1
        channel2.set_volume(c2v)  # Half volume for track 2

        # Play with crossfade by adjusting volumes over time
        if (not GPIO.input(22)):
            if c1v == 1:
                c1v = 0
            else:
                c1v += 0.05
            channel1.set_volume(c1v)
            time.sleep(1)
        if (not GPIO.input(23)):
            if c2v == 1:
                c2v = 0
            else:
                c2v += 0.05
            channel1.set_volume(c2v)
            time.sleep(1)
        if (not GPIO.input(27)):
            playing = False

    # Stop the tracks
    channel1.stop()
    channel2.stop()

    # Quit Pygame
    pygame.quit()
