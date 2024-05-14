import os
import pygame,pigame
import RPi.GPIO as GPIO
import time


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

# Set up the display
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Dual Channel Music Player')
font = pygame.font.Font(None, 18)
background_color = (30, 30, 30)
text_color = (255, 255, 255)
highlight_color = (255, 200, 0)

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
buttons = {
    'quit': 27,       # Stop playing/Quit button
    'select': 17,     # Select song button
    'scroll': 22,     # Scroll down through the list
    'switch': 23      # Switch between lists
}
for button in buttons.values():
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize the mixer
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
channels = [pygame.mixer.Channel(0), pygame.mixer.Channel(1)]

# Directory containing tracks
music_directory = 'audio_files'
songs = sorted([f for f in os.listdir(music_directory) if f.endswith('.wav')])
indexes = [0, 0]  # Indexes for each channel's current selection
active_list = 0   # Index of the currently active list

# Function to play a song
def play_song(channel, index):
    track = pygame.mixer.Sound(os.path.join(music_directory, songs[index]))
    channel.play(track)

# Function to draw the menu
def draw_menu():
    screen.fill(background_color)
    y_offset = 16
    for i, song in enumerate(songs):
        for j in range(2):
            x_offset = 50 + j * 350
            color = highlight_color if indexes[j] == i and j == active_list else text_color
            text_surf = font.render(f'> {song}' if indexes[j] == i else song, True, color)
            screen.blit(text_surf, (x_offset, y_offset + i * 40))
    pygame.display.flip()

# Callback functions for GPIO
def handle_quit(channel):
    pygame.quit()
    GPIO.cleanup()
    global code_run
    code_run = False
    exit()

def handle_select(channel):
    channels[active_list].stop()  # Stop the current song if any
    play_song(channels[active_list], indexes[active_list])

def handle_scroll(channel):
    indexes[active_list] = (indexes[active_list] + 1) % len(songs)
    draw_menu()

def handle_switch(channel):
    global active_list
    active_list = 1 - active_list  # Toggle between 0 and 1
    draw_menu()

# Attach callbacks
GPIO.add_event_detect(buttons['quit'], GPIO.FALLING, callback=handle_quit, bouncetime=300)
GPIO.add_event_detect(buttons['select'], GPIO.FALLING, callback=handle_select, bouncetime=300)
GPIO.add_event_detect(buttons['scroll'], GPIO.FALLING, callback=handle_scroll, bouncetime=300)
GPIO.add_event_detect(buttons['switch'], GPIO.FALLING, callback=handle_switch, bouncetime=300)

# Initial draw
draw_menu()

# Keep the application running
code_run = True
try:
    while code_run:
        time.sleep(0.1)  # Prevents CPU from spinning
finally:
    GPIO.cleanup()  # Ensure GPIO resources are freed on exit
