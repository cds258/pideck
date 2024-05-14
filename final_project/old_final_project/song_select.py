import os
import pygame
import time
import RPi.GPIO as GPIO

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Music Player')
font = pygame.font.Font(None, 36)
background_color = (30, 30, 30)
text_color = (255, 255, 255)
highlight_color = (255, 200, 0)

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Start/Stop button
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Volume up
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Volume down
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Stop playing
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Next song
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Previous song
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Select song

# Initialize the mixer
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)

# Directory containing tracks
music_directory = '/path/to/your/music/folder'  # Change this to your folder path
songs = sorted([f for f in os.listdir(music_directory) if f.endswith('.wav')])  # Assuming WAV for reliable playback
current_index = 0

# Function to play a song
def play_song(index):
    global channel1
    channel1.stop()
    track = pygame.mixer.Sound(os.path.join(music_directory, songs[index]))
    channel1.play(track, loops=-1)

# Create separate channels for each track
channel1 = pygame.mixer.Channel(0)

# Function to draw the menu
def draw_menu():
    screen.fill(background_color)
    for i, song in enumerate(songs):
        if i == current_index:
            text_surf = font.render(f'> {song}', True, highlight_color)
        else:
            text_surf = font.render(song, True, text_color)
        screen.blit(text_surf, (50, 30 + i * 40))
    pygame.display.flip()

# Initial draw
draw_menu()

# Main loop to handle button presses
try:
    while True:
        if not GPIO.input(18):  # Select button
            play_song(current_index)
            time.sleep(0.5)  # Debounce delay

        if not GPIO.input(24):  # Next song
            current_index = (current_index + 1) % len(songs)
            draw_menu()
            time.sleep(0.5)  # Debounce delay

        if not GPIO.input(25):  # Previous song
            current_index = (current_index - 1) % len(songs)
            draw_menu()
            time.sleep(0.5)  # Debounce delay

        if not GPIO.input(27):  # Stop playing
            channel1.stop()
            print("Playback stopped.")
            break

finally:
    pygame.quit()
    GPIO.cleanup()

