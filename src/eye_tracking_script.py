import time
import os
import random
from datetime import datetime
import pandas as pd
import screeninfo
import tobii_research as tr
import keyboard
import sys


# Get screen resolution
screen = screeninfo.get_monitors()[0]
screen_width, screen_height = screen.width, screen.height
screen_resolution = f"{screen_width}x{screen_height}p"

# Create 'data' folder if it doesn't exist
data_folder = 'data/gaze'
os.makedirs(data_folder, exist_ok=True)

# List to store gaze data during the session
gaze_data_list = []

# Try to find the eye tracker
eyetrackers = tr.find_all_eyetrackers()
my_eyetracker = eyetrackers[0] if eyetrackers else None
use_mock_data = len(eyetrackers) == 0

if use_mock_data:
    print("No eye tracker found. Generating mock gaze data...")
else:
    my_eyetracker = eyetrackers[0]
    print(f"Connected to Eye Tracker: {my_eyetracker.model} ({my_eyetracker.serial_number})")

# Smoothed gaze coordinates (to prevent flickering)
smoothed_x, smoothed_y = screen_width // 2, screen_height // 2 

def generate_mock_gaze():
    """
    Generates random gaze data when no tracker is available.
    Author: Thomas Pichardo

    """
    return random.uniform(0.1, 0.8), random.uniform(0.1, 0.8)

def gaze_data_callback(gaze_data):
    """
    Processes and stores real-time or mock gaze data.
    Author: Thomas Pichardo
    
    """
    global smoothed_x, smoothed_y
    now = datetime.now()
    unix_time = int(time.time()*1000)  # Get current Unix time in seconds

    if use_mock_data:
        left_gaze_x, left_gaze_y = generate_mock_gaze()
        right_gaze_x, right_gaze_y = generate_mock_gaze()
    else:
        left_gaze_x, left_gaze_y = gaze_data.get('left_gaze_point_on_display_area', (None, None))
        right_gaze_x, right_gaze_y = gaze_data.get('right_gaze_point_on_display_area', (None, None))

    # Calculate average gaze position if valid
    if None not in (left_gaze_x, left_gaze_y, right_gaze_x, right_gaze_y):
        avg_x = (left_gaze_x + right_gaze_x) / 2
        avg_y = (left_gaze_y + right_gaze_y) / 2
    else:
        avg_x, avg_y = generate_mock_gaze()  # Fallback to mock data if real data is missing

    # Convert to screen coordinates
    smoothed_x = int(avg_x * screen_width)
    smoothed_y = int(avg_y * screen_height)

    gaze_data_list.append({
        "unix_time": unix_time,
        "left_gaze_x": left_gaze_x,
        "left_gaze_y": left_gaze_y,
        "right_gaze_x": right_gaze_x,
        "right_gaze_y": right_gaze_y,
        "screen_x": smoothed_x,
        "screen_y": smoothed_y,
        "screen_resolution": screen_resolution
    })

if not use_mock_data:
    my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

def load_calibration(eye_tracker):
    """
    Loads and applies the last saved calibration for the eye tracker.

    Parameters:
    eye_tracker (EyeTracker): The eye tracker device from which to retrieve calibration data.

    Side Effects:
    - Loads and applies calibration data to avoid re-calibration.
    - Prints success or failure message.

    Author: Mauro van Hulst
    """
    calibration_data = eye_tracker.retrieve_calibration_data()
    
    if calibration_data is not None:
        eye_tracker.apply_calibration_data(calibration_data)
        print("Calibration loaded successfully from the eye tracker.")
    else:
        print("No calibration found or failed to retrieve calibration.")

# Load the calibration
load_calibration(my_eyetracker)

def get_gaze_data():
    """Unified function: Returns smoothed gaze data for visualization."""
    return smoothed_x, smoothed_y

print('Recording gaze data... Press F12 to stop.')

try:
    while not keyboard.is_pressed("f12"):
        if use_mock_data:
            gaze_data_callback({})
        time.sleep(1/60)  # Simulating 60 Hz data collection
finally:
    if not use_mock_data:
        my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

    if not gaze_data_list:
        print("No gaze data recorded. Check if the eye tracker is detecting gaze.")
    else:
        file_path = os.path.join(data_folder, 'gaze_data_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.csv')
        df = pd.DataFrame(gaze_data_list)
        df.to_csv(file_path, index=False)
        print(f'Gaze data saved to: {file_path}')
