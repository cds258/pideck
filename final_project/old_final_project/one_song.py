import pygame
import time

# Initialize pygame
pygame.init()

# Setup the mixer to play audio
pygame.mixer.init()

# Load your MP3 file
pygame.mixer.music.load('Music.mp3')

# Play the MP3 file
pygame.mixer.music.play()

# Since the playing is non-blocking, we wait until the music is done playing
while pygame.mixer.music.get_busy():
    time.sleep(1)

# Optional: Stop the mixer
pygame.mixer.music.stop()
pygame.quit()
