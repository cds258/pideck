import os
import pygame
import RPi.GPIO as GPIO
import time

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Dual Channel Music Player')
font = pygame.font.Font(None, 36)
background_color = (30, 30, 30)
text_color = (255, 255, 255)
highlight_color = (255, 200, 0)

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
buttons = {
    'play1': 17, 'play2': 22,
    'next1': 24, 'prev1': 25,
    'next2': 23, 'prev2': 18
}
for button in buttons.values():
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize the mixer
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
channel1 = pygame.mixer.Channel(0)
channel2 = pygame.mixer.Channel(1)

# Directory containing tracks
music_directory = '/path/to/your/music/folder'
songs = sorted([f for f in os.listdir(music_directory) if f.endswith('.wav')])
current_index = [0, 0]  # Indexes for channel 1 and 2

# Function to play a song
def play_song(channel, index):
    track = pygame.mixer.Sound(os.path.join(music_directory, songs[index]))
    channel.play(track)

# Function to draw the menu
def draw_menu():
    screen.fill(background_color)
    y_offset = 30
    for i, song in enumerate(songs):
        for j in range(2):
            x_offset = 50 + j * 350
            color = highlight_color if current_index[j] == i else text_color
            text_surf = font.render(f'> {song}' if current_index[j] == i else song, True, color)
            screen.blit(text_surf, (x_offset, y_offset + i * 40))
    pygame.display.flip()

def button_callback(channel):
    global current_index
    button_name = {v: k for k, v in buttons.items()}[channel]
    ch, action = button_name[-1], button_name[:-1]
    
    if action == 'play':
        play_song(channel1 if ch == '1' else channel2, current_index[int(ch)-1])
    elif action == 'next':
        current_index[int(ch)-1] = (current_index[int(ch)-1] + 1) % len(songs)
        draw_menu()
    elif action == 'prev':
        current_index[int(ch)-1] = (current_index[int(ch)-1] - 1) % len(songs)
        draw_menu()

# Attach callbacks
for button, pin in buttons.items():
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=button_callback, bouncetime=300)

# Initial draw
draw_menu()

# Keep the application running
try:
    while True:
        time.sleep(0.1)  # Prevents CPU from spinning
finally:
    pygame.quit()
    GPIO.cleanup()
