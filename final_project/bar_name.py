import os
import pygame
import RPi.GPIO as GPIO
import time
from pydub.utils import mediainfo
from pydub import AudioSegment


from io import BytesIO
import tempfile

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
font = pygame.font.Font(None, 25)
background_color = (30, 30, 30)
text_color = (255, 255, 255)
highlight_color = (255, 200, 0)
outline_color = (255, 255, 0)  # Yellow outline for visibility


# Encoder 1
pin_a1 = 20  # Encoder 1 pin A
pin_b1 = 21  # Encoder 1 pin B
# Encoder 2
pin_a2 = 13  # Encoder 2 pin A
pin_b2 = 6  # Encoder 2 pin B

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
buttons = {'quit': 27, 'select': 17, 'scroll': 22, 'switch': 23, 
'A1' :pin_a1, 'B1': pin_b1, 'A2': pin_a2, 'B2': pin_b2 }

for button in buttons.values():
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize the mixer
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
channels = [pygame.mixer.Channel(0), pygame.mixer.Channel(1)]
music_directory = 'audio_files'
songs = sorted([f for f in os.listdir(music_directory) if f.endswith('.wav')])
indexes = [0, 0]  # Indexes for each channel's current selection
currently_playing = [0, 0]
active_list = 0   # Initialize active_list

# Load durations using Pydub
def get_durations(songs, music_directory):
    durations = []
    for song in songs:
        song_path = os.path.join(music_directory, song)
        audio_info = mediainfo(song_path)
        duration = float(audio_info['duration'])
        durations.append(duration)
    return durations

song_durations = get_durations(songs, music_directory)
start_times = [None, None]  # Start times for each song
label_max = 25

def play_song(channel_index, song_index):
    track = pygame.mixer.Sound(os.path.join(music_directory, songs[song_index]))
    channels[channel_index].play(track)
    start_times[channel_index] = time.time()
    currently_playing[channel_index] = song_index

def draw_menu():
    screen.fill(background_color)
    y_offset = 16
    for i, song in enumerate(songs):
        for j in range(2):  # Assuming two channels
            x_offset = 50 + j * 350
            is_active = indexes[j] == i and j == active_list
            color = highlight_color if is_active else text_color
            song_label = f'> {song}' if is_active else song
            if len(song_label) > label_max:
                song_label = song_label[:label_max]
            text_surf = font.render(song_label, True, color)
            screen.blit(text_surf, (x_offset, y_offset + i * 40))

    # Draw progress bars with outlines and current song names
    bar_height = 20
    bar_width = 300
    for j in range(2):
        bar_x = 50 + j * 350
        bar_y = y_offset + len(songs) * 40 + 30 + 40  # Additional space for song name text
        if channels[j].get_busy() and start_times[j] is not None:
            # Display the current song name
            current_song_name = songs[currently_playing[j]]
            if len(current_song_name) > label_max:
                current_song_name = current_song_name[:label_max]
            song_name_surf = font.render(current_song_name, True, highlight_color)
            screen.blit(song_name_surf, (bar_x, bar_y - 40))  # Position above the progress bar

            # Calculate and draw the progress bar
            elapsed_time = time.time() - start_times[j]
            progress = elapsed_time / song_durations[j]
            bar_length = int(progress * bar_width)
            pygame.draw.rect(screen, highlight_color, (bar_x, bar_y, bar_length, bar_height))
            pygame.draw.rect(screen, outline_color, (bar_x, bar_y, bar_width, bar_height), 2)  # Outline
    
    pygame.display.flip()

def handle_quit(channel):
    pygame.quit()
    GPIO.cleanup()
    exit()

def handle_select(channel):
    channels[active_list].stop()
    play_song(active_list, indexes[active_list])

def handle_scroll(channel):
    indexes[active_list] = (indexes[active_list] + 1) % len(songs)
    draw_menu()

def scroll_wheel(id, amt):
    indexes[id] = (indexes[id] + amt) % len(songs)
    draw_menu()


def handle_switch(channel):
    global active_list
    active_list = 1 - active_list
    draw_menu()


#GPIO.setup([pin_a1, pin_b1, pin_a2, pin_b2], GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Counters for each encoder
counter1 = 0
last_state1 = None
counter2 = 0
last_state2 = None

# Callback function for Encoder 1
def rotary_callback1(channel):
    global counter1, last_state1
    state_a = GPIO.input(pin_a1)
    state_b = GPIO.input(pin_b1)
    if state_a and state_b:
        if last_state1 == "CW":
            counter1 -= 1
            scroll_wheel(0,-1)
        elif last_state1 == "CCW":
            counter1 += 1
            scroll_wheel(0,1)
        #print("Encoder 1 Counter: ", counter1)
    elif state_a and not state_b:
        last_state1 = "CW"
    elif not state_a and state_b:
        last_state1 = "CCW"

# Callback function for Encoder 2
def rotary_callback2(channel):
    global counter2, last_state2
    state_a = GPIO.input(pin_a2)
    state_b = GPIO.input(pin_b2)
    if state_a and state_b:
        if last_state2 == "CW":
            counter2 += 1
            scroll_wheel(1,1)
        elif last_state2 == "CCW":
            counter2 -= 1
            scroll_wheel(1,-1)
       # print("Encoder 2 Counter: ", counter2)
    elif state_a and not state_b:
        last_state2 = "CW"
    elif not state_a and state_b:
        last_state2 = "CCW"



# Attach callbacks
GPIO.add_event_detect(buttons['quit'], GPIO.FALLING, callback=handle_quit, bouncetime=300)
GPIO.add_event_detect(buttons['select'], GPIO.FALLING, callback=handle_select, bouncetime=300)
GPIO.add_event_detect(buttons['scroll'], GPIO.FALLING, callback=handle_scroll, bouncetime=300)
GPIO.add_event_detect(buttons['switch'], GPIO.FALLING, callback=handle_switch, bouncetime=300)
# Add event detection for both encoders
GPIO.add_event_detect(pin_a1, GPIO.BOTH, callback=rotary_callback1, bouncetime=2)
GPIO.add_event_detect(pin_b1, GPIO.BOTH, callback=rotary_callback1, bouncetime=2)
GPIO.add_event_detect(pin_a2, GPIO.BOTH, callback=rotary_callback2, bouncetime=2)
GPIO.add_event_detect(pin_b2, GPIO.BOTH, callback=rotary_callback2, bouncetime=2)


draw_menu()
try:
    while True:
        draw_menu()
        time.sleep(0.1)
finally:
    GPIO.cleanup()
