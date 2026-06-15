from pynput import mouse, keyboard
import time
import csv
from datetime import datetime
import os
import screeninfo
import math

# Create a 'data' folder if it doesn't exist
data_folder = 'data/input/'
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

screen = screeninfo.get_monitors()[0]
screen_resolution = f"{screen.width}x{screen.height}p"  # Example screen resolution

# Define the CSV file path with a timestamp
file_path = os.path.join(data_folder, 'input_log_' + datetime.now().strftime('%d-%m-%Y_%H-%M-%S') + '.csv')
# Create or open a CSV file
with open(file_path, 'a', newline='') as file:
    writer = csv.writer(file)

    # Threshold values
    movement_threshold = 100  # Log only if the mouse moves more than 10 pixels
    last_logged_position = None  # To keep track of the last logged mouse position  

    # Write the header with Unix timestamp, event type, screen resolution, and duration
    writer.writerow(['timestamp', 'unix_time', 'event_type', 'details_x', 'details_y', 'duration', 'screen_resolution'])

    # Dictionaries to store the start times for key and mouse press events
    key_start_times = {}
    button_start_times = {}

    def log_and_print(event_type, details_x=None, details_y=None, duration=None, *args):
        """
        Logs and prints details of an event with timestamp and additional metadata.

        Args:
            event_type (str): Type of the event (e.g., 'key_press', 'mouse_click', 'mouse_move').
            details_x (int or str, optional): X-coordinate or related detail of the event. Defaults to None.
            details_y (int or str, optional): Y-coordinate or related detail of the event. Defaults to None.
            duration (float, optional): Duration of the event in seconds. Defaults to None.
            *args: Additional details for the event.

        Prints:
            A formatted message including the timestamp, event type, coordinates, screen resolution, and duration.

        Writes:
            Logs the event details into a CSV file.

        Author: Maikel Boezer
        """
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Format time to include milliseconds
        unix_time = int(now.timestamp())  # Get Unix timestamp as an integer
        
        message = f"{timestamp} - {event_type}: {' '.join(map(str, args))} | X: {details_x}, Y: {details_y} | Resolution: {screen_resolution} | Duration: {duration if duration else 'N/A'}"
        print(message)
        
        # Write to CSV, with None placeholders for unused values (e.g., key presses)
        writer.writerow([timestamp, unix_time, event_type, details_x, details_y, duration, screen_resolution])

    def on_press(key):
        """
        Handles key press events by recording the start time of the key press.

        Args:
            key (Key): The key that was pressed.

        Records:
            The start time of the key press in `key_start_times` to calculate its duration later.
        
        Author: Maikel Boezer
        """
        key_str = str(key)  # Ensure consistency by converting the key to a string
        if key_str not in key_start_times:  # Only log the first press
            key_start_times[key_str] = time.time()  # Log the start time for the key press

    def on_release(key):
        """
        Handles key release events by calculating and logging the duration of the key press.

        Args:
            key (Key): The key that was released.

        Logs:
            The event type ('key_press'), key, and duration if the start time is recorded.

        Stops:
            If the 'F12' key is released, stops the listener.

        Author: Maikel Boezer
        """
        key_str = str(key)  # Ensure consistency by converting the key to a string
        start_time = key_start_times.pop(key_str, None)
        if start_time:
            duration = round(time.time() - start_time, 3)  # Calculate duration
            log_and_print('key_press', key_str, None, duration)

        if key == keyboard.Key.f12:  # Stop when the 'F12' key is pressed
            return False  # This will stop the listener

    def on_click(x, y, button, pressed):
        """
        Handles mouse click events by logging the click details and duration.

        Args:
            x (int): X-coordinate of the mouse click.
            y (int): Y-coordinate of the mouse click.
            button (Button): The mouse button pressed or released.
            pressed (bool): True if the button is pressed, False if released.

        Logs:
            The event type ('mouse_click'), coordinates, button, and duration of the click.

        Author: Maikel Boezer
        """
        button_str = str(button)  # Ensure consistency by converting the button to a string
        if pressed:
            if button_str not in button_start_times:  # Only log the first press
                button_start_times[button_str] = time.time()  # Log the start time for the button press
        else:
            start_time = button_start_times.pop(button_str, None)
            if start_time:
                duration = round(time.time() - start_time, 3)  # Calculate duration
                log_and_print('mouse_click', x, y, duration, button)

    def on_move(x, y):
        """
        Handles mouse movement events by logging positions if the movement exceeds a threshold.

        Args:
            x (int): Current X-coordinate of the mouse pointer.
            y (int): Current Y-coordinate of the mouse pointer.

        Logs:
            The event type ('mouse_move'), current coordinates if the movement exceeds the defined threshold.

        Author: Maikel Boezer
        """
        global last_logged_position
        if last_logged_position is None:
            # Log the first movement
            last_logged_position = (x, y)
            log_and_print('mouse_move', x, y)
        else:
            last_x, last_y = last_logged_position
            distance_moved = math.sqrt((x - last_x) ** 2 + (y - last_y) ** 2)
            
            if distance_moved > movement_threshold:
                # Log the movement only if it exceeds the threshold
                last_logged_position = (x, y)
                log_and_print('mouse_move', x, y)

    # Set up listeners
    with mouse.Listener(on_click=on_click, on_move=on_move) as mouse_listener, keyboard.Listener(on_press=on_press, on_release=on_release) as keyboard_listener:
        keyboard_listener.join()  # This will block until the 'F12' key is pressed
        print(f"saving data to {file_path}")
