import time
import pandas as pd
import os
import glob
import subprocess
import threading
from pynput import keyboard
import whisper
import torch
import nltk
from nltk.tokenize import sent_tokenize

# Paths to folders for OBS recordings, audio output, and CSV output
obs_recording_folder = "C:/Users/Cedri/OneDrive/Documents/BUas/Year 3/Semester 1/video_data"
output_audio_folder = "C:/Users/Cedri/OneDrive/Documents/BUas/Year 3/Semester 1/audio_data"
output_timestamps_folder = "C:/Users/Cedri/OneDrive/Documents/BUas/Year 3/Semester 1/recording_timestamps"
output_transcript_folder = "C:/Users/Cedri/OneDrive/Documents/BUas/Year 3/Semester 1/output_transcripts"

# Initialize timestamps list and flag for tracking
timestamps = []
tracking = False
tracking_thread = None

### 1. Function to track Unix time while recording ###
def track_time():
    """Track Unix time each second while recording."""
    while tracking:
        timestamps.append(int(time.time()))  # Add current Unix time
        print(f"Tracking Unix time: {timestamps[-1]}")  # Print the latest timestamp
        time.sleep(1)  # Sleep for 1 second between timestamps

def on_press(key):
    """Detect keypress events to start and stop time tracking."""
    global tracking, tracking_thread
    try:
        if key == keyboard.Key.f12:  # Detect F12 key press
            if not tracking:
                print("F12 pressed. Starting Unix time tracking...")
                tracking = True
                tracking_thread = threading.Thread(target=track_time)
                tracking_thread.start()
            else:
                print("F12 pressed. Stopping Unix time tracking...")
                tracking = False  # Stop tracking
                tracking_thread.join()  # Wait for the thread to finish
                return False  # Stop the listener after tracking ends
    except AttributeError:
        pass

# Prompt to indicate the script is ready
print("Ready to track. Press F12 to start recording...")

# Start the key listener to detect F12 presses
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

# Save Unix timestamps to DataFrame after tracking finishes
df_timestamps = pd.DataFrame(timestamps, columns=['unixtime'])

# Get the latest OBS recording filename to use for audio extraction and CSV naming
list_of_files = glob.glob(os.path.join(obs_recording_folder, '*.mkv'))
if list_of_files:
    latest_file = max(list_of_files, key=os.path.getmtime)
    filename_without_extension = os.path.splitext(os.path.basename(latest_file))[0]
    print(f"Latest OBS recording found: {latest_file}")

    ### 2. Extract mic input from the OBS recording using FFmpeg ###
    output_audio_path = os.path.join(output_audio_folder, f"{filename_without_extension}_mic_audio.wav")
    
    # FFmpeg command to extract audio track 0:2 (mic input) to a .wav file
    ffmpeg_command = [
        'ffmpeg',
        '-y',               # Overwrite the output file if it exists
        '-i', latest_file,   # Input video file
        '-map', '0:2',       # Map audio stream 0:2 (mic input)
        '-vn',               # Ignore video stream
        '-acodec', 'pcm_s16le',  # WAV codec
        '-ar', '48000',      # Sample rate (same as input)
        '-ac', '2',          # Number of channels (stereo)
        output_audio_path    # Output .wav file
    ]

    # Run the FFmpeg command
    subprocess.run(ffmpeg_command)
    print(f"Mic input extracted to {output_audio_path}")

    ### 3. Transcribe the extracted audio using Whisper ###
    print("Checking if GPU is available for Whisper...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model("base", device=device)
    print(f"Using device: {device}")

    # Transcribe the .wav audio file using Whisper (focused on English)
    result = model.transcribe(output_audio_path, language="en")
    print("Transcription complete.")

    ### 4. Tokenize the transcription into sentences ###
    nltk.download('punkt')
    nltk.download('punkt_tab')

    # Tokenize the transcription into sentences
    sentences = sent_tokenize(result['text'])
    print(f"Sentence tokenization complete.")

    ### 5. Save the transcription to a CSV file ###
    df_transcript = pd.DataFrame({
        'sentence': sentences
    })

    # Save the transcription DataFrame as a CSV file
    transcript_csv_path = os.path.join(output_transcript_folder, f"{filename_without_extension}_transcript.csv")
    df_transcript.to_csv(transcript_csv_path, index=False)
    print(f"Transcription saved to {transcript_csv_path}")

    ### 6. Save the Unix time DataFrame as a CSV file ###
    csv_path = os.path.join(output_timestamps_folder, f"{filename_without_extension}_timestamps.csv")
    df_timestamps.to_csv(csv_path, index=False)
    print(f"Unix timestamps saved to {csv_path}")

else:
    print(f"No recordings found in {obs_recording_folder}.")
