# Speech-to-Text Script with Hugging Face Whisper

import os
import subprocess
import pandas as pd
import torch
import nltk
from nltk.tokenize import sent_tokenize
from transformers import pipeline
import logging
from datetime import timedelta
import numpy as np
from moviepy.editor import VideoFileClip
from scipy.io import wavfile

# Setup logging for better feedback
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Helper function to clean paths
def clean_path(path: str) -> str:
    return path.strip('"').strip("'")

# Define folder path where videos are saved
video_folder = r"C:\Users\Cedri\OneDrive\Documents\BUas\Year 3\Semester 1\video_data2" # Replace with the path to the video folder
output_audio_folder = r"C:\Users\Cedri\OneDrive\Documents\BUas\Year 3\Semester 1\audio_data2" # Replace with the path to the audio folder
output_csv_folder = r"C:\Users\Cedri\OneDrive\Documents\BUas\Year 3\Semester 1\test2" # Replace with the path to the output CSV folder

# Ensure the output directories exist
os.makedirs(output_audio_folder, exist_ok=True)
os.makedirs(output_csv_folder, exist_ok=True)

# Get the latest .mkv video file from the folder
video_files = [f for f in os.listdir(video_folder) if f.endswith('.mkv')]
if not video_files:
    raise FileNotFoundError("No .mkv video files found in the specified folder.")
latest_video = max(video_files, key=lambda f: os.path.getmtime(os.path.join(video_folder, f)))
video_path = os.path.join(video_folder, latest_video)

# Function to extract audio using FFmpeg
def extract_audio(video_path: str, output_audio_path: str) -> bool:
    try:
        ffmpeg_command = [
            'ffmpeg',
            '-y',
            '-i', video_path,
            '-map', '0:2',
            '-vn',
            '-acodec', 'pcm_s16le',
            '-ar', '48000',
            '-ac', '2',
            output_audio_path
        ]
        subprocess.run(ffmpeg_command, check=True)
        logging.info(f"Mic input extracted to {output_audio_path}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running FFmpeg: {e}")
        return False

# Generate the audio file path
filename_without_extension = os.path.splitext(os.path.basename(video_path))[0]
output_audio_path = os.path.join(output_audio_folder, f"{filename_without_extension}_mic_audio.wav")

# Run the audio extraction
logging.info('Starting audio extraction...')
extract_audio(video_path, output_audio_path)
logging.info('Audio extraction completed.')

# Load the larger Whisper model for better transcription accuracy
logging.info("Loading Hugging Face Whisper model (medium version)...")
device = "cuda" if torch.cuda.is_available() else "cpu"
whisper_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-medium", device=0 if device == "cuda" else -1)

# Transcribe the audio
logging.info("Transcribing audio with the medium Whisper model...")
result = whisper_pipeline(output_audio_path, return_timestamps=True)
transcription = result.get('text', "")
timestamps = result.get('chunks', [])
logging.info("Transcription complete")

# Function to get the duration of the video
def get_video_duration(video_path: str) -> float:
    clip = VideoFileClip(video_path)
    duration = clip.duration  # Duration in seconds
    clip.close()
    return duration

# Get the actual video duration
video_duration = get_video_duration(video_path)
logging.info(f"Video duration calculated: {video_duration} seconds")

# Function to post-process timestamps to avoid resets
def post_process_timestamps(timestamps: list) -> list:
    last_end_time = 0.0
    for i, chunk in enumerate(timestamps):
        start_time, end_time = chunk['timestamp']
        if start_time < last_end_time:
            duration = end_time - start_time
            start_time = last_end_time
            end_time = start_time + duration
            timestamps[i]['timestamp'] = (start_time, end_time)
        last_end_time = end_time
    return timestamps

# Convert seconds to HH:MM:SS format
def format_time(seconds: float) -> str:
    return str(timedelta(seconds=round(seconds)))

# Process and format timestamps
fixed_timestamps = post_process_timestamps(timestamps)
for chunk in fixed_timestamps:
    start_time, end_time = chunk['timestamp']
    chunk['start_time'] = start_time  # Keep as float for further processing
    chunk['end_time'] = end_time      # Keep as float for further processing
    del chunk['timestamp']            # Remove the original 'timestamp' tuple

# Function to correct drift incrementally after each segment
def adjust_timestamps_no_duplicates(timestamps, buffer=0.5):
    adjusted_timestamps = []
    last_end_time = 0.0
    seen_texts = set()

    for chunk in timestamps:
        # Ensure that start_time and end_time are in float format for processing
        if isinstance(chunk['start_time'], str):
            start_time = pd.Timedelta(chunk['start_time']).total_seconds()
        else:
            start_time = float(chunk['start_time'])
        
        if isinstance(chunk['end_time'], str):
            end_time = pd.Timedelta(chunk['end_time']).total_seconds()
        else:
            end_time = float(chunk['end_time'])

        # Skip adding duplicates if the same text has been seen before within a short time frame
        if chunk['text'] in seen_texts:
            continue
        seen_texts.add(chunk['text'])

        # If there's a significant gap (true silence), insert it; otherwise, adjust to skip drift
        if start_time - last_end_time > buffer:
            adjusted_timestamps.append({
                'start_time': format_time(last_end_time),
                'end_time': format_time(start_time),
                'text': '[Silence]'
            })

        adjusted_timestamps.append({
            'start_time': format_time(start_time),
            'end_time': format_time(end_time),
            'text': chunk['text']
        })
        last_end_time = end_time

    return adjusted_timestamps

# Function to correct drift incrementally after each segment
def synchronize_timestamps_incrementally(timestamps, video_duration):
    synchronized_timestamps = []
    cumulative_drift = 0.0
    last_end_time = 0.0

    for chunk in timestamps:
        # Convert start_time and end_time to float
        if isinstance(chunk['start_time'], str):
            start_time = pd.Timedelta(chunk['start_time']).total_seconds()
        else:
            start_time = float(chunk['start_time'])

        if isinstance(chunk['end_time'], str):
            end_time = pd.Timedelta(chunk['end_time']).total_seconds()
        else:
            end_time = float(chunk['end_time'])

        # Calculate drift after each segment and adjust accordingly
        if last_end_time != 0.0:
            expected_start_time = last_end_time
            drift = start_time - expected_start_time
            cumulative_drift += drift
            logging.info(f"Recalibrating: Drift of {drift} seconds at segment starting at {start_time}")

        # Clamp cumulative drift to ensure it doesn't lead to negative timestamps or overflow
        cumulative_drift = max(min(cumulative_drift, 10.0), -10.0)  # Limit drift correction to ±10 seconds

        # Adjust the start and end times based on cumulative drift
        start_time = max(0.0, start_time - cumulative_drift)
        end_time = max(0.0, end_time - cumulative_drift)

        # Append adjusted chunk
        synchronized_timestamps.append({
            'start_time': format_time(start_time),
            'end_time': format_time(end_time),
            'text': chunk['text']
        })

        last_end_time = end_time

    return synchronized_timestamps

# Improved function to fill in moments of silence with proper end coverage
def fill_silences_with_end_coverage(timestamps: list, video_duration: float, max_silence_duration=5.0) -> list:
    filled_timestamps = []
    last_end_time = 0.0

    for chunk in timestamps:
        # Ensure that start_time and end_time are in float format for processing
        if isinstance(chunk['start_time'], str):
            start_time = pd.Timedelta(chunk['start_time']).total_seconds()
        else:
            start_time = float(chunk['start_time'])
        
        if isinstance(chunk['end_time'], str):
            end_time = pd.Timedelta(chunk['end_time']).total_seconds()
        else:
            end_time = float(chunk['end_time'])

        # Detect true silence and split if it exceeds max_silence_duration
        if start_time - last_end_time > max_silence_duration:
            silence_start = last_end_time
            while silence_start < start_time:
                silence_end = min(silence_start + max_silence_duration, start_time)
                filled_timestamps.append({
                    'start_time': format_time(silence_start),
                    'end_time': format_time(silence_end),
                    'text': '[Silence]'
                })
                silence_start = silence_end

        # Add the current chunk
        filled_timestamps.append({
            'start_time': format_time(start_time),
            'end_time': format_time(end_time),
            'text': chunk['text']
        })
        last_end_time = end_time

    # Add a final silence segment if the last spoken part doesn't reach the end of the video
    if last_end_time < video_duration:
        filled_timestamps.append({
            'start_time': format_time(last_end_time),
            'end_time': format_time(video_duration),
            'text': '[Silence]'
        })

    return filled_timestamps

# Apply the new incremental synchronization for drift correction
logging.info('Adjusting timestamps to remove duplicates and fix drift...')
adjusted_timestamps = adjust_timestamps_no_duplicates(fixed_timestamps)
logging.info('Timestamps adjusted successfully.')
logging.info('Synchronizing timestamps incrementally to correct drift...')
synchronized_timestamps = synchronize_timestamps_incrementally(adjusted_timestamps, video_duration)
logging.info('Timestamps synchronized successfully.')

# Improved silence handling to ensure coverage until the end of the video
logging.info('Filling in silences and ensuring coverage to the end of the video...')
final_timestamps = fill_silences_with_end_coverage(synchronized_timestamps, video_duration)
logging.info('Silences filled successfully.')

# Tokenize the transcription into sentences
nltk.download('punkt')
sentences = sent_tokenize(transcription)
logging.info("Tokenized sentences created")

# Create the final DataFrame with start and end times for each row
logging.info('Creating DataFrame with final timestamps and transcriptions...')
df_output = pd.DataFrame(final_timestamps)
logging.info('DataFrame created successfully.')

# Save the final DataFrame as a CSV file
output_csv_path = os.path.join(output_csv_folder, f"{filename_without_extension}_output.csv")
logging.info('Saving the final output to CSV file...')
df_output.to_csv(output_csv_path, index=False)
logging.info('CSV file saved successfully.')
logging.info(f"Output with refined timestamps and silence filtering saved to {output_csv_path}")