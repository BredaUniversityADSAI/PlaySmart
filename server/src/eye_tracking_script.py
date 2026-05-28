import time
import os
from datetime import datetime
import pandas as pd
import screeninfo
import tobii_research as tr
import keyboard
import random

# Find the Eye tracker
eyetrackers = tr.find_all_eyetrackers()
use_mock_gaze = len(eyetrackers) == 0

# Check if any eye trackers are found
if use_mock_gaze:
    print("No eye tracker found. Using mock gaze data.")
else:
    my_eyetracker = eyetrackers[0]
    print("Connected to:", my_eyetracker.model)
    print("Address: " + my_eyetracker.address)
    print("Name: " + my_eyetracker.device_name)
    print("Serial number: " + my_eyetracker.serial_number)

# Get screen resolution
screen = screeninfo.get_monitors()[0]
screen_resolution = f"{screen.width}x{screen.height}p"

# Ensure 'data/gaze' folder exists
data_folder = 'data/gaze'
os.makedirs(data_folder, exist_ok=True)

# List to store gaze data during the session
gaze_data_list = []

def gaze_data_callback(gaze_data):
    """Processes and stores real-time gaze data."""
    now = datetime.utcnow()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    unix_time = int(now.timestamp())

    left_gaze_x = gaze_data['left_gaze_point_on_display_area'][0]
    left_gaze_y = gaze_data['left_gaze_point_on_display_area'][1]
    right_gaze_x = gaze_data['right_gaze_point_on_display_area'][0]
    right_gaze_y = gaze_data['right_gaze_point_on_display_area'][1]

    gaze_data_list.append({
        "timestamp": timestamp,
        "unix_time": unix_time,
        "left_gaze_x": left_gaze_x,
        "left_gaze_y": left_gaze_y,
        "right_gaze_x": right_gaze_x,
        "right_gaze_y": right_gaze_y,
        "screen_resolution": screen_resolution
    })

def generate_mock_gaze_data():
    """Generates random gaze data."""
    now = datetime.utcnow()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    unix_time = int(now.timestamp())

    return {
        "timestamp": timestamp,
        "unix_time": unix_time,
        "left_gaze_x": random.uniform(0, 1),
        "left_gaze_y": random.uniform(0, 1),
        "right_gaze_x": random.uniform(0, 1),
        "right_gaze_y": random.uniform(0, 1),
        "screen_resolution": screen_resolution
    }

if use_mock_gaze:
    print("Generating mock gaze data. Press F12 to stop.")
    while not keyboard.is_pressed('f12'):
        mock_data = generate_mock_gaze_data()
        print(f"Mock Data: {mock_data}")  # Debugging
        gaze_data_list.append(mock_data)
        time.sleep(0.6)
else:
    def load_calibration(eye_tracker):
        calibration_data = eye_tracker.retrieve_calibration_data()
        if calibration_data:
            eye_tracker.apply_calibration_data(calibration_data)
            print("Calibration loaded successfully.")
        else:
            print("No calibration found.")

    load_calibration(my_eyetracker)
    my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)
    print("Connected to eye tracker. Press F12 to stop.")

    while not keyboard.is_pressed('f12'):
        time.sleep(0.6)

    my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
    print("Disconnected from eye tracker.")

if gaze_data_list:
    file_path = os.path.join(data_folder, 'gaze_data_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.csv')
    df = pd.DataFrame(gaze_data_list)
    df.to_csv(file_path, index=False)
    print(f"Gaze data saved to: {file_path}")
else:
    print("Warning: No gaze data collected!")
