from pynput import mouse, keyboard
import time
import csv
from datetime import datetime
import os
import screeninfo
import math

screen = screeninfo.get_monitors()[0]
screen_resolution = f"{screen.width}x{screen.height}p"

# Generate a single timestamped filename for the session
session_timestamp = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
data_folder = 'data/input/'
os.makedirs(data_folder, exist_ok=True)
file_path = os.path.join(data_folder, f'input_log_{session_timestamp}.csv')

movement_threshold = 100
last_logged_position = None
key_start_times = {}
button_start_times = {}

def get_unix_time():
    return int(time.time() * 1000)

def log_and_print(event_type, details_x=None, details_y=None, duration=None):
    unix_time = get_unix_time()
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(['unix_time', 'event_type', 'details_x', 'details_y', 'duration', 'screen_resolution'])
            print(f"CSV Header Written: {file_path}")
        writer.writerow([unix_time, event_type, details_x, details_y, duration, screen_resolution])
        print(f"Logging event: {event_type}, X: {details_x}, Y: {details_y}, Duration: {duration}")

def on_press(key):
    key_str = str(key)
    if key_str not in key_start_times:
        key_start_times[key_str] = time.time()

def on_release(key):
    key_str = str(key)
    if key == keyboard.Key.f12:
        print("F12 pressed, stopping recording.")
        mouse_listener.stop()  # stop mouse too
        return False           # stop keyboard
    start_time = key_start_times.pop(key_str, None)
    if start_time:
        duration = round(time.time() - start_time, 3)
        log_and_print('key_press', key_str, None, duration)

def on_click(x, y, button, pressed):
    if pressed:
        log_and_print('mouse_click', x, y)

def on_move(x, y):
    global last_logged_position
    if last_logged_position is None:
        last_logged_position = (x, y)
        log_and_print('mouse_move', x, y)
    else:
        last_x, last_y = last_logged_position
        distance_moved = math.sqrt((x - last_x) ** 2 + (y - last_y) ** 2)
        if distance_moved > movement_threshold:
            last_logged_position = (x, y)
            log_and_print('mouse_move', x, y)

print("Keyboard & Mouse logging started. Press F12 to stop.")

# create the listeners so both can be stopped
mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move)
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

# start both
mouse_listener.start()
keyboard_listener.start()

# wait for keyboard to finish (when F12 pressed)
keyboard_listener.join()

print(f"Saving data to {file_path}")
