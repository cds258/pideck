import os
import pygame,pigame
import RPi.GPIO as GPIO
import time
import numpy as np
import wave
import struct


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


pygame.display.set_caption('Dual Channel Music Player with Real-Time Waveform')
font = pygame.font.Font(None, 18)
background_color = (30, 30, 30)
text_color = (255, 255, 255)
highlight_color = (255, 200, 0)
waveform_color = (0, 150, 255)
playback_marker_color = (255, 0, 0)

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
pygame.mixer.init()
channels = [pygame.mixer.Channel(0), pygame.mixer.Channel(1)]

# Directory containing tracks
music_directory = 'audio_files'
songs = sorted([f for f in os.listdir(music_directory) if f.endswith('.wav')])
indexes = [0, 0]
active_list = 0

# Load audio data and prepare waveform data
waveforms = []

def load_waveforms():
    for song in songs:
        filepath = os.path.join(music_directory, song)
        with wave.open(filepath, 'rb') as wav_file:
            frames = wav_file.readframes(-1)
            # Convert bytes to numpy array based on audio format
            if wav_file.getsampwidth() == 2:
                data = np.frombuffer(frames, dtype=np.int16)
            else:
                data = np.frombuffer(frames, dtype=np.uint8)
            if wav_file.getnchannels() == 2:
                data = data[::2] + data[1::2]  # Convert stereo to mono by averaging
            waveforms.append((wav_file.getframerate(), np.interp(data, (data.min(), data.max()), (0, 100))))

load_waveforms()

def play_song(channel, index):
    channel.stop()
    track = pygame.mixer.Sound(os.path.join(music_directory, songs[index]))
    channel.play(track)

def draw_waveform(index, position, playback_position=None):
    rate, waveform = waveforms[index]
    waveform_length = len(waveform)
    x_scale = 350 / waveform_length  # scale to 350 pixels width
    y_offset = 550

    # Draw waveform
    for i in range(1, waveform_length):
        pygame.draw.line(screen, waveform_color, (x_scale * (i - 1) + position, y_offset - waveform[i - 1]),
                         (x_scale * i + position, y_offset - waveform[i]))

    # Draw playback position
    if playback_position is not None:
        playback_x = position + x_scale * playback_position
        pygame.draw.line(screen, playback_marker_color, (playback_x, y_offset - 100), (playback_x, y_offset))

def draw_menu():
    screen.fill(background_color)
    for i, song in enumerate(songs):
        text_surf = font.render(song, True, highlight_color if indexes[active_list] == i else text_color)
        screen.blit(text_surf, (50, 16 + i * 40))
    if pygame.mixer.Channel(active_list).get_busy():
        # Update waveform with playback marker
        pos = pygame.mixer.Channel(active_list).get_pos() / 1000  # Get position in seconds
        rate, _ = waveforms[indexes[active_list]]
        playback_position = int(pos * rate)  # Convert seconds to sample index
        draw_waveform(indexes[active_list], 50 + active_list * 350, playback_position)
    pygame.display.flip()

# Callback functions for GPIO
def handle_quit(channel):
    pygame.quit()
    GPIO.cleanup()
    global code_run
    code_run = False

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
