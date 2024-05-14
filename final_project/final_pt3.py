import os
import pygame
import RPi.GPIO as GPIO
import time
import pigame
from pydub.utils import mediainfo
from pydub import AudioSegment
import serial
import threading

os.putenv('SDL_VIDEODRV', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV', 'dummy')
os.putenv('SDL_MOUSEDEV', '/dev/null')
os.putenv('DISPLAY', '')

# Initialize Pygame
pygame.init()
pitft = pigame.PiTft()
size = width, height = 320, 240
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Dual Channel Music Player')
font = pygame.font.Font(None, 20)
font2 = pygame.font.Font(None, 15)
background_color = (30, 30, 30)
text_color = (255, 255, 255)
highlight_color = (255, 200, 0)
outline_color = (255, 255, 0)  # Yellow outline for visibility

#Initialize PauseL
pauseL = False
firstL = True
paused_timeL = 0.0
paused_initL = 0.0
elapsed_timeL = 0.0
#Initialize PauseR
pauseR = False
firstR = True
paused_timeR = 0.0
paused_initR = 0.0
elapsed_timeR = 0.0

# Encoder 1
pin_a1 = 20  # Encoder 1 pin A
pin_b1 = 21  # Encoder 1 pin B
# Encoder 2
pin_a2 = 13  # Encoder 2 pin A
pin_b2 = 6  # Encoder 2 pin B


# Initialize GPIO
GPIO.setmode(GPIO.BCM)
buttons = {'quit': 27, 'sound1': 17, 'sound2': 22, 'sound3': 23, 
'A1' :pin_a1, 'B1': pin_b1, 'A2': pin_a2, 'B2': pin_b2 }

for button in buttons.values():
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize the mixer
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
channels = [pygame.mixer.Channel(0), pygame.mixer.Channel(1), pygame.mixer.Channel(2)]
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
label_max = 20

def play_song(channel_index, song_index):
    track = pygame.mixer.Sound(os.path.join(music_directory, songs[song_index]))
    channels[channel_index].play(track)
    start_times[channel_index] = time.time()
    currently_playing[channel_index] = song_index

def draw_menu():
    global paused_timeL, firstL, elapsed_timeL, pauseL, paused_initL, paused_timeR, firstR, elapsed_timeR, pauseR, paused_initR
    screen.fill(background_color)
    y_offset = 8
    for i, song in enumerate(songs):
        for j in range(2):  # Assuming two channels
            x_offset = 10 + j * 150
            is_active = indexes[j] == i #and j == active_list
            color = highlight_color if is_active else text_color
            song_label = f'> {song}' if is_active else song
            if len(song_label) > label_max:
                song_label = song_label[:label_max]
            text_surf = font.render(song_label, True, color)
            screen.blit(text_surf, (x_offset, y_offset + i * 20))

    # Draw progress bars with outlines and current song names
    bar_height = 20
    bar_width = 140
    for j in range(2):
        bar_x = 10 + j * 150
        bar_y = y_offset + len(songs) * 20 + 20  # Additional space for song name text
        if channels[j].get_busy() and start_times[j] is not None:
            # Display the current song name
            current_song_name = songs[currently_playing[j]]
            if len(current_song_name) > label_max:
                current_song_name = current_song_name[:label_max]
            song_name_surf = font2.render(current_song_name, True, highlight_color)
            screen.blit(song_name_surf, (bar_x, bar_y - 15))  # Position above the progress bar

            # Calculate and draw the progress bar
            if j == 0:
                if pauseL:
                    if firstL:
                        paused_initL = time.time()
                        firstL = False
                    else:
                        paused_timeL = time.time() - paused_initL
                else:
                    if paused_timeL != 0:
                        firstL = True
                        start_times[j] += paused_timeL
                        paused_timeL, paused_initL = 0,0
                    elapsed_timeL = time.time() - start_times[j]
                # progress = elapsed_timeL / song_durations[j]
            else: 
                if pauseR:
                    if firstR:
                        paused_initR = time.time()
                        firstR = False
                    else:
                        paused_timeR = time.time() - paused_initR
                else:
                    if paused_timeR != 0:
                        firstR = True
                        start_times[j] += paused_timeR
                        paused_timeR, paused_initR = 0,0
                    elapsed_timeR = time.time() - start_times[j]
                # progress = elapsed_timeR / song_durations[j]
            progress = elapsed_timeL / song_durations[j] if j == 0 else elapsed_timeR / song_durations[j]
            bar_length = int(progress * bar_width)
            pygame.draw.rect(screen, highlight_color, (bar_x, bar_y, bar_length, bar_height))
            pygame.draw.rect(screen, outline_color, (bar_x, bar_y, bar_width, bar_height), 2)  # Outline
    
    pygame.display.flip()
    pitft.update()

def handle_quit(channel):
    pygame.quit()
    GPIO.cleanup()
    del(pitft)
    import sys
    sys.exit(0)
    exit()

def handle_select(channel):
    channels[active_list].stop()
    play_song(active_list, indexes[active_list])

def handle_scroll(channel):
    indexes[active_list] = (indexes[active_list] + 1) % len(songs)
    draw_menu()

def scroll_wheel(id, amt):
    #print(f"scroll {id},{amt}")
    global indexes, songs
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

#define volume parameters
vol = 1



count0 = 0
count1 = 0

clk0LastState = GPIO.input(pin_a1)
clk1LastState = GPIO.input(pin_a2)

def handle_rotary0():
        global count0, clk0LastState
        clk0State = GPIO.input(pin_a1)
        dt0State = GPIO.input(pin_b1)
        if clk0State != clk0LastState:
                if dt0State != clk0State:
                        count0 += 1
                        scroll_wheel(0,-1)
                else:
                        count0 -= 1
                        scroll_wheel(0,1)
                #print(f"count0: {count0}")
        clk0LastState = clk0State

def handle_rotary1():
        global count1, clk1LastState
        clk1State = GPIO.input(pin_a2)
        dt1State = GPIO.input(pin_b2)
        if clk1State != clk1LastState:
                if dt1State != clk1State:
                        count1 += 1
                        scroll_wheel(1,1)
                else:
                        count1 -= 1
                        scroll_wheel(1,-1)
                #print(f"count1: {count1}")
        clk1LastState = clk1State


# Callback function for Encoder 1
def rotary_callback1():
    #print("rcb1")
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
def rotary_callback2():
    #print("rcb2")
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

def sound_effect1(channel):
    # Stop any current playback on the new channel
    channels[2].stop()
    # Play the sound effect on the new channel
    sound_effect = pygame.mixer.Sound('/home/pi/final_project/sound1.wav')
    channels[2].play(sound_effect)

def sound_effect2(channel):
    # Stop any current playback on the new channel
    channels[2].stop()
    # Play the sound effect on the new channel
    sound_effect = pygame.mixer.Sound('/home/pi/final_project/sound2.wav')
    channels[2].play(sound_effect)

def sound_effect3(channel):
    # Stop any current playback on the new channel
    channels[2].stop()
    # Play the sound effect on the new channel
    sound_effect = pygame.mixer.Sound('/home/pi/final_project/sound3.wav')
    channels[2].play(sound_effect)


# Attach callbacks
GPIO.add_event_detect(buttons['quit'], GPIO.FALLING, callback=handle_quit, bouncetime=300)
GPIO.add_event_detect(buttons['sound1'], GPIO.FALLING, callback=sound_effect1, bouncetime=300)
GPIO.add_event_detect(buttons['sound2'], GPIO.FALLING, callback=sound_effect2, bouncetime=300)
GPIO.add_event_detect(buttons['sound3'], GPIO.FALLING, callback=sound_effect3, bouncetime=300)
# Add event detection for both encoders
# GPIO.add_event_detect(pin_a1, GPIO.BOTH, callback=rotary_callback1, bouncetime=100)
# GPIO.add_event_detect(pin_b1, GPIO.BOTH, callback=rotary_callback1, bouncetime=100)
# GPIO.add_event_detect(pin_a2, GPIO.BOTH, callback=rotary_callback2, bouncetime=100)
# GPIO.add_event_detect(pin_b2, GPIO.BOTH, callback=rotary_callback2, bouncetime=100)


GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

ch1_pause = False
ch2_pause = False
ch1_play = False
ch2_play = False

def left_left_cb(channel):
    # CH1 Select
    #print("CH1 Select")
    global ch1_play, ch1_pause
    if not ch1_pause:
      channels[0].stop()
      play_song(0, indexes[0])
      ch1_play = True

def left_right_cb(channel):
    # CH1  Pause
    #print("CH1 Pause")
    global ch1_pause, pauseL, ch1_play
    if(ch1_pause):
        channels[0].unpause()
        ch1_pause = False
        ch1_play = True
        pauseL = False
    else:
        channels[0].pause()
        if (ch1_play):
          pauseL = True
          ch1_pause = True
          ch1_play = False
        
def right_left_cb(channel):
    # CH2 Pause
    #print("CH2 Pause")
    global ch2_pause, pauseR, ch2_play
    if(ch2_pause):
        channels[1].unpause()
        ch2_pause = False
        ch2_play = True
        pauseR = False
    else:
        channels[1].pause()
        if ch2_play:
          ch2_pause = True
          pauseR = True
          ch2_play = False

def right_right_cb(channel):
    # CH2 Select
    #print("CH2 Select")
    global ch2_play, ch2_pause
    if not ch2_pause:
      channels[1].stop()
      play_song(1, indexes[1])
      ch2_play = True

GPIO.add_event_detect(26, GPIO.RISING, callback=left_right_cb, bouncetime=200)
GPIO.add_event_detect(19, GPIO.RISING, callback=left_left_cb, bouncetime=200)
GPIO.add_event_detect(12, GPIO.RISING, callback=right_right_cb, bouncetime=200)
GPIO.add_event_detect(16, GPIO.RISING, callback=right_left_cb, bouncetime=200)

def inc_volume(channel):
  global vol
  vol *= 1.1

def dec_volume(channel):
  global vol
  vol /= 1.1


GPIO.add_event_detect(5, GPIO.RISING, callback=inc_volume, bouncetime=200)
GPIO.add_event_detect(4, GPIO.RISING, callback=dec_volume, bouncetime=200)

def map_value(x, original_max=29.35, target_max=1):
    return x / original_max
    
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.reset_input_buffer()


data = {'pot#l' : 0.5, 'pot#r': 0.5, 'pot#c': 0.5}
def update_volumes():
    # Calculate the effective volume for each channel
    # Channel 1 (Left) fades in as pot#c goes from 0 to 1
    # Channel 0 (Right) fades out as pot#c goes from 0 to 1
    left_volume = vol * data['pot#l'] * data['pot#c']  # Increases as pot#c goes from 0 to 1
    right_volume = vol * data['pot#r'] * (1 - data['pot#c'])  # Decreases as pot#c goes from 0 to 1

    # Set the volumes
    channels[1].set_volume(left_volume)
    channels[0].set_volume(right_volume)




def rotary_encoder_thread():
    global counter1, last_state1, counter2, last_state2

    global count0, clk0LastState, count1, clk1LastState
    while True:
        handle_rotary0()
        handle_rotary1()
        # rotary_callback1()
        # rotary_callback2()
        #thread.sleep(0.01)


# Create and start the rotary encoder thread
rotary_thread = threading.Thread(target=rotary_encoder_thread)
rotary_thread.daemon = True
rotary_thread.start()


try:
    while True:
       
        
        draw_menu()
        
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').rstrip()
            if line:
                try:
                    # Split the line by commas and filter out empty strings
                    entries = filter(None, line.split(','))
                    # Loop through each non-empty entry and parse it
                    for entry in entries:
                        # Split the entry into key and value parts
                        key, value = entry.split(':')
                        # Clean up any whitespace and convert value to float
                        key = key.strip()
                        value = float(value.strip())
                        data[key] = map_value(value)
                    # Now you can use the data dictionary for further processing
                  #  print(data)  # Example usage
                    update_volumes()
                except ValueError as e:
                    print(f"Error parsing line: {line}, Error: {e}")
        
       # thread.sleep(0.01)

except:
    print("Caught exception")
    GPIO.cleanup()        
finally:
    GPIO.cleanup()
    del(pitft)

