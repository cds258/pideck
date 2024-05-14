import os
import pygame
import RPi.GPIO as GPIO
import time
from pydub.utils import mediainfo

os.putenv('SDL_VIDEODRV', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV', 'dummy')
os.putenv('SDL_MOUSEDEV', '/dev/null')
os.putenv('DISPLAY', '')

# Initialize Pygame
pygame.init()
size = width, height = 800, 600
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Dual Channel Music Player')
font = pygame.font.Font(None, 36)
background_color = (30, 30, 30)
text_color = (255, 255, 255)
highlight_color = (255, 200, 0)

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
buttons = {'quit': 27, 'select': 17, 'scroll': 22, 'switch': 23}
for button in buttons.values():
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize the mixer
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
channels = [pygame.mixer.Channel(0), pygame.mixer.Channel(1)]
music_directory = 'audio_files'
songs = sorted([f for f in os.listdir(music_directory) if f.endswith('.wav')])

# Function to get the duration of each song
def get_durations(songs, music_directory):
    durations = []
    for song in songs:
        song_path = os.path.join(music_directory, song)
        audio_info = mediainfo(song_path)
        duration = float(audio_info['duration'])
        durations.append(duration)
    return durations

song_durations = get_durations(songs, music_directory)
indexes = [0, 0]  # Indexes for each channel's current selection
start_times = [None, None]  # Start times for each song
active_list = 0 

# Function to play a song and set the timer for a specific channel index
def play_song(channel_index, song_index):
    track = pygame.mixer.Sound(os.path.join(music_directory, songs[song_index]))
    channels[channel_index].play(track)
    start_times[channel_index] = time.time()

# Adjusted draw_menu to use channel indices directly for timers
def draw_menu():
    screen.fill(background_color)
    y_offset = 20
    # Display each song
    for i, song in enumerate(songs):
        for j in range(2):  # Assuming two channels
            x_offset = 50 + j * 350
            is_active = indexes[j] == i and j == active_list
            color = highlight_color if is_active else text_color
            song_label = f'> {song}' if is_active else song
            text_surf = font.render(song_label, True, color)
            screen.blit(text_surf, (x_offset, y_offset + i * 40))
    
    # Draw progress bars
    bar_height = 20
    for j in range(2):
        if channels[j].get_busy() and start_times[j] is not None:
            elapsed_time = time.time() - start_times[j]
            progress = elapsed_time / song_durations[j]
            bar_length = int(progress * 300)  # Width of the progress bar
            pygame.draw.rect(screen, highlight_color, (50 + j * 350, y_offset + len(songs) * 40 + 30, bar_length, bar_height))
    
    pygame.display.flip()

# Callback functions for GPIO
def handle_quit(channel):
    pygame.quit()
    GPIO.cleanup()
    exit()

def handle_select(channel):
    channels[active_list].stop()  # Stop the current song if any
    play_song(active_list, indexes[active_list])

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
try:
    while True:
        draw_menu()  # Update the screen with timer
        time.sleep(0.1)  # Refresh rate
finally:
    GPIO.cleanup()  # Ensure GPIO resources are freed on exit
