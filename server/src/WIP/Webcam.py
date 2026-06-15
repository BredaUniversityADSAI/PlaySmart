import subprocess
import os
import pandas as pd 
import glob
import time
from datetime import datetime
import sys
import keyboard 

# Path to the OpenFace FeatureExtraction executable
openface_executable = 'OpenFace_2.2.0_win_x64\FeatureExtraction.exe'  

# Output directory for the extracted features
output_dir = 'output'  # Creates an output folder in the current directory

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Capture the Start time of the Recording during the process
start_time = datetime.now()

# Convert the recording start time to Unix timestamp
start_time_unix = int(start_time.timestamp())  # Unix time in seconds


# Run OpenFace FeatureExtraction on webcam (device 0)
command = [
    openface_executable,
    '-device', '0',        # Use the default webcam
    '-out_dir', output_dir,  # Output directory for the CSV files
    '-aus'                 # Extract Action Units (facial muscle movements related to emotions)
]

# function to block Q key
def block_q_key(event):
    if event.name == 'q':
        return False

# F12 to stop recording
def stop_recording():
    print('Stopping webcam recording...')
    process.terminate() # Terminating OpenFace process
    print('Webcam recording stopped.')

# Set up keyboard listeners
keyboard.hook(block_q_key)
keyboard.add_hotkey('f12', stop_recording)

# Run the command
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Read the output stream to capture the start time message
for line in process.stdout:
    print(line.strip())
    if "Starting tracking" in line:
        # Break the loop when the start message is found
        break
    
try:
    while process.poll() is None:
        time.sleep(0.1)  
except KeyboardInterrupt:
    process.terminate()

process.wait()  # Wait for the process to complete

print(f"OpenFace processing finished. Outputs saved in: {output_dir}")
print(f"Recording start time: {start_time}")

# Automatically detect the latest CSV file
csv_files = glob.glob(os.path.join(output_dir, '*.csv'))
if csv_files:
    latest_csv = max(csv_files, key=os.path.getctime)
    print(f"Loading data from: {latest_csv}")

    # Load the CSV file using pandas
    df = pd.read_csv(latest_csv)
    
    # Print column names to verify
    print("Columns in DataFrame:", df.columns)

    # Strip any leading or trailing spaces from column names
    df.columns = df.columns.str.strip()
    
    # Display the first few rows of the extracted data
    print("\nData extracted from OpenFace (first 5 rows):")
    print(df.head())
    
    # Define emotion mapping function
    def map_emotion(row):
        try:
            # Adjust these column names based on your actual DataFrame columns
            if row.get('AU06_c', 0) == 1 and row.get('AU12_c', 0) == 1 and row.get('AU25_c', 0) == 1:
                return 'Happiness'
            elif row.get('AU01_c', 0) == 1 and row.get('AU04_c', 0) == 1 and row.get('AU15_c', 0) == 1 and row.get('AU17_c', 0) == 1:
                return 'Sadness'
            elif row.get('AU05_c', 0) == 1 and row.get('AU26_c', 0) == 1 and row.get('AU02_c', 0) == 1 and row.get('AU07_c', 0) == 1:
                return 'Surprise'
            elif row.get('AU09_c', 0) == 1 and row.get('AU10_c', 0) == 1 and row.get('AU14_c', 0) == 1:
                return 'Disgust'
            elif row.get('AU01_c', 0) == 1 and row.get('AU02_c', 0) == 1 and row.get('AU04_c', 0) == 1 and row.get('AU05_c', 0) == 1 and row.get('AU07_c', 0) == 1:
                return 'Fear'
            elif row.get('AU04_c', 0) == 1 and row.get('AU07_c', 0) == 1 and row.get('AU23_c', 0) == 1 and row.get('AU25_c', 0) == 1:
                return 'Anger'
            else:
                return 'Neutral'
        except KeyError as e:
            print(f"Missing column in DataFrame: {e}")
            return 'Unknown'

    # Apply the emotion mapping function
    df['emotion'] = df.apply(map_emotion, axis=1)
    
    # Convert timestamps to Unix time based on the recording start time
    def convert_to_unix_time(relative_timestamp, start_unix_time):
        try:
            # Add the relative timestamp to the start Unix time
            return int(round(start_unix_time + relative_timestamp))
        except ValueError:
            return float('nan')

    # Ensure the timestamp column is in the correct format
    df['timestamp'] = df['timestamp'].astype(float)
    
    # Apply Unix time conversion
    df['unix_time'] = df['timestamp'].apply(lambda ts: convert_to_unix_time(ts, start_time_unix))

    # Converting unix time to readable datetime format
    df['timestamp'] = pd.to_datetime(df['unix_time'], unit='s')

    # Keep only specific columns
    df = df[['timestamp', 'unix_time', 'emotion', 'confidence']]  # Adjust as needed


    # Save the DataFrame to a CSV file in the 'data' folder
    data_folder = 'data'
    file_path = os.path.join(data_folder, 'webcam_data_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.csv')
    df.to_csv(file_path, index=False)
    print(f"Updated CSV saved to: {file_path}")

else:
    print(f"No CSV files found in {output_dir}")