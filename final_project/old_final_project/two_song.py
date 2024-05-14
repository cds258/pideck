import pygame

# Initialize Pygame
pygame.init()

# Initialize the mixer
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)

# Load two MP3 tracks
track1 = pygame.mixer.Sound('Music.wav')
track2 = pygame.mixer.Sound('Yup_I_Guess.wav')

# Create separate channels for each track
channel1 = pygame.mixer.Channel(0)
channel2 = pygame.mixer.Channel(1)

# Play both tracks
channel1.play(track1)
channel2.play(track2)

# Example controls
import time

# Set volume (0.0 to 1.0)
channel1.set_volume(0.5)  # Half volume for track 1
channel2.set_volume(0.5)  # Half volume for track 2

# Play with crossfade by adjusting volumes over time
for i in range(10):
    # Increase volume of track 1, decrease volume of track 2
    vol1 = 0.1 * i
    vol2 = 1 - vol1
    channel1.set_volume(vol1)
    channel2.set_volume(vol2)
    time.sleep(1)  # Delay to simulate crossfade effect

# Stop the tracks
channel1.stop()
channel2.stop()

# Quit Pygame
pygame.quit()
