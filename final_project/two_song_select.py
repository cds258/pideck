import os
import pygame,pigame
import RPi.GPIO as GPIO
import time


# Pygame and Screen Setup
os.putenv('SDL_VIDEODRV','fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV','dummy')
os.putenv('SDL_MOUSEDEV','/dev/null')
os.putenv('DISPLAY','')

# Initialize Pygame
pygame.init()
pitft = pigame.PiTft()
size = width, height = 320, 240
screen = pygame.display.set_mode(size)

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption('Dual Channel Music Player')
font = pygame.font.Font(None, 36)
background_color = (30, 30, 30)
text_color = (255, 255, 255)
highlight_color = (255, 200, 0)

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Play/Stop button for channel 1
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Play/Stop button for channel 2
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Next song for channel 1
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Previous song for channel 1
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Next song for channel 2
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Previous song for channel 2

# Initialize the mixer
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
channel1 = pygame.mixer.Channel(0)
channel2 = pygame.mixer.Channel(1)

# Directory containing tracks
music_directory = '/path/to/your/music/folder'
songs = sorted([f for f in os.listdir(music_directory) if f.endswith('.wav')])

# Track selection indices
current_index_1 = 0
current_index_2 = 0

# Function to play a song
def play_song(channel, index):
    track = pygame.mixer.Sound(os.path.join(music_directory, songs[index]))
    channel.play(track)

# Function to draw the menu
def draw_menu():
    screen.fill(background_color)
    y_offset = 30
    for i, song in enumerate(songs):
        if i == current_index_1:
            text_surf = font.render(f'> {song}', True, highlight_color)
        else:
            text_surf = font.render(song, True, text_color)
        screen.blit(text_surf, (50, y_offset + i * 40))

        if i == current_index_2:
            text_surf = font.render(f'> {song}', True, highlight_color)
        else:
            text_surf = font.render(song, True, text_color)
        screen.blit(text_surf, (400, y_offset + i * 40))
    pygame.display.flip()

# Initial draw
draw_menu()

# Main loop to handle button presses
try:
    while True:
        if not GPIO.input(17):  # Select button for channel 1
            play_song(channel1, current_index_1)
            time.sleep(0.5)  # Debounce delay

        if not GPIO.input(22):  # Select button for channel 2
            play_song(channel2, current_index_2)
            time.sleep(0.5)  # Debounce delay

        if not GPIO.input(23):  # Next song for channel 1
            current_index_1 = (current_index_1 + 1) % len(songs)
            draw_menu()
            time.sleep(0.5)  # Debounce delay

        if not GPIO.input(25):  # Previous song for channel 1
            current_index_1 = (current_index_1 - 1) % len(songs)
            draw_menu()
            time.sleep(0.5)  # Debounce delay

        if not GPIO.input(27):  # Next song for channel 2
            current_index_2 = (current_index_2 + 1) % len(songs)
            draw_menu()
            time.sleep(0.5)  # Debounce delay

        if not GPIO.input(18):  # Previous song for channel 2
            current_index_2 = (current_index_2 - 1) % len(songs)
            draw_menu()
            time.sleep(0.5)  # Debounce delay

finally:
    pygame.quit()
    GPIO.cleanup()
