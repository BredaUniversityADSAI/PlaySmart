import os
import glob
import datetime
import tkinter as tk
from tkinter import simpledialog
import random
import string
import json
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server.python_app.sftp_upload import upload_file_to_sftp

def get_latest_file(path):
    """
    Get the most recently modified CSV file in the specified directory.

    Args:
        path (str): The directory path to search for CSV files.

    Returns:
        str: The path of the latest CSV file, or None if no files are found.

    Author: Mauro van Hulst
    """
    # Get a list of all CSV files in the directory
    files = glob.glob(os.path.join(path, "*.csv"))
    
    # Sort files by modification time
    latest_file = max(files, key=os.path.getmtime, default=None)
    return latest_file


def generate_random_string(length=8):
    """
    Generate a random string of letters and digits.

    Args:
        length (int): Length of the random string.

    Returns:
        str: A random string of specified length.

    Author: Maikel Boezer
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def load_mapping(mapping_file='data/json/ign_mapping.json'):
    """
    Load an existing mapping from a JSON file.

    Args:
        mapping_file (str): Path to the mapping JSON file.

    Returns:
        dict: A dictionary of existing mappings.

    Author: Maikel Boezer
    """
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r') as file:
            return json.load(file)
    return {}


def save_mapping(mapping, mapping_file='data/json/ign_mapping.json'):
    """
    Save the mapping dictionary to a JSON file with pretty printing.
    
    Args:
        mapping (dict): The mapping dictionary to save.
        mapping_file (str): Path to the mapping JSON file.

    Author: Maikel Boezer
    """
    with open(mapping_file, 'w') as file:
        json.dump(mapping, file, indent=4)


def get_latest_video(path):
    """
    Get the most recently modified video file (e.g., MP4) in the specified directory.

    Args:
        path (str): The directory path to search for video files.

    Returns:
        str: The path of the latest video file, or None if no files are found.

    Author: Mauro van Hulst
    """
    # Get a list of all video files (e.g., MP4) in the directory
    video_files = glob.glob(os.path.join(path, "*.mp4"))  # Assuming MP4 format; modify for other video formats if necessary
    
    # Sort files by modification time
    latest_video = max(video_files, key=os.path.getmtime, default=None)
    return latest_video


def load_daily_game_count(count_file='data/json/date_game_count.json'):
    """
    Load the daily game count mapping from a JSON file.

    Args:
        count_file (str): Path to the game count JSON file.

    Returns:
        dict: A dictionary with dates and game names as keys and their counts as values.

    Author: Mauro van Hulst
    """
    if os.path.exists(count_file):
        try:
            with open(count_file, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"Warning: {count_file} is empty or corrupted. Initializing as empty.")
            return {}
    return {}


def save_daily_game_count(daily_game_count, count_file='data/json/date_game_count.json'):
    """
    Save the daily game count mapping to a JSON file.

    Args:
        daily_game_count (dict): A dictionary with dates, game names, and their counts.
        count_file (str): Path to the game count JSON file.

    Author: Mauro van Hulst
    """
    with open(count_file, 'w') as file:
        json.dump(daily_game_count, file, indent=4)


def update_daily_game_count(game_name, count_file='data/json/date_game_count.json'):
    """
    Update the daily game count for the specified game and return the ordinal prefix.

    Args:
        game_name (str): The name of the game to update the count for.
        count_file (str): Path to the game count JSON file.

    Returns:
        str: The ordinal string based on the new count for the game for today.

    Author: Mauro van Hulst
    """
    # Get today's date in "yyyy-mm-dd" format
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    
    # Load the existing daily game counts
    daily_game_count = load_daily_game_count(count_file)
    
    # If today is not in the file, start a new dictionary for today
    if today not in daily_game_count:
        daily_game_count[today] = {}
    
    # Get the count for the current game, or start at 0
    game_count = daily_game_count[today].get(game_name, 0) + 1
    
    # Update the count for the current game
    daily_game_count[today][game_name] = game_count
    
    # Save the updated daily counts
    save_daily_game_count(daily_game_count, count_file)
    
    # Get the ordinal string for the current count
    ordinal_prefix = get_ordinal(game_count)
    
    return ordinal_prefix, today


def get_ordinal(n):
    """
    Convert an integer into its ordinal representation (e.g., 1 -> first, 2 -> second, etc.).

    Args:
        n (int): The integer to convert.

    Returns:
        str: The ordinal string.

    Author: Mauro van Hulst
    """
    return f"{n}{'th' if 4<=n%100<=20 else {1:'st',2:'nd',3:'rd'}.get(n%10, 'th')}"


def process_file_merged(filename, player_name, game_name, save_directory, mapping_file='data/json/ign_mapping.json', video_directory='C:/Users/mauro/Videos', count_file='data/json/date_game_count.json', video_save_directory='data/video'):
    """
    Process the file by renaming it according to a specific pattern with game count, player ID, game name, and timestamp.
    Also renames the most recent video file to match the processed file name and moves it to a specified directory.

    Args:
        filename (str): The original filename to process.
        player_name (str): The player's in-game name to map.
        game_name (str): The name of the game.
        mapping_file (str): Path to the mapping JSON file.
        save_directory (str): Directory to save the processed file.
        video_directory (str): Directory to find the most recent video file.
        count_file (str): Path to the daily game count JSON file.
        video_save_directory (str): Directory to save the renamed video file.

    Author: Maikel Boezer, Mauro van Hulst
    """
    # Load existing mappings
    mapping = load_mapping(mapping_file)
    
    # Get or generate the player ID (e.g., P006)
    if player_name not in mapping:
        mapping[player_name] = generate_random_string()
    player_id = mapping[player_name]
    
    # Get the ordinal prefix for today's game count and today's date
    ordinal_prefix, today = update_daily_game_count(game_name, count_file)
    
    # Get the current time (hours, minutes, seconds)
    current_time = datetime.datetime.now().strftime("%H-%M-%S")
    
    # Construct the new filename
    new_filename = f"{ordinal_prefix}_game_{player_id}_{game_name}_{today}_{current_time}.csv"
    
    # Save the updated mapping
    save_mapping(mapping, mapping_file)
    
    # Change the save directory for the renamed file
    new_filepath = os.path.join(save_directory, new_filename)
    
    # Read the file and process
    with open(filename, 'r') as file:
        content = file.read()
    
    # Save the content to the new file in the specified directory
    with open(new_filepath, 'w') as new_file:
        new_file.write(content)

    # Delete the old file
    os.remove(filename)
    
    print(f"Processed '{filename}' -> '{new_filepath}' and deleted the old file.")

    # Rename the most recent video file to match the new CSV file name
    latest_video = get_latest_video(video_directory)
    if latest_video:
        # Ensure the video save directory exists
        os.makedirs(video_save_directory, exist_ok=True)
        
        new_video_filename = f"{ordinal_prefix}_game_{player_id}_{game_name}_{today}_{current_time}.mp4"
        new_video_filepath = os.path.join(video_save_directory, new_video_filename)
        
        # Move and rename the video file
        os.rename(latest_video, new_video_filepath)
        print(f"Renamed video '{latest_video}' -> '{new_video_filepath}'")
    else:
        print("No video file found in the specified directory.")

def process_file(filename, player_name, game_name, save_directory, mapping_file='data/json/ign_mapping.json'):
    """
    Process the file by renaming it according to a specific pattern with game count, player ID, game name, and timestamp.
    Also renames the most recent video file to match the processed file name and moves it to a specified directory.

    Args:
        filename (str): The original filename to process.
        player_name (str): The player's in-game name to map.
        game_name (str): The name of the game.
        mapping_file (str): Path to the mapping JSON file.
        save_directory (str): Directory to save the processed file.

    Author: Maikel Boezer, Mauro van Hulst
    """
    # Load existing mappings
    mapping = load_mapping(mapping_file)
    
    # Get or generate the player ID (e.g., P006)
    if player_name not in mapping:
        mapping[player_name] = generate_random_string()
    player_id = mapping[player_name]
    
    # Extract the base name (e.g., "input_log") from the original filename
    original_base_name = os.path.basename(filename).split('_')[0]
    
    # Get the current time (hours, minutes, seconds)
    current_time = datetime.datetime.now().strftime("%H-%M-%S")
    
    # Construct the new filename
    new_filename = f"{player_id}_{original_base_name}_data_{game_name}_{current_time}.csv"
    
    # Save the updated mapping
    save_mapping(mapping, mapping_file)
    
    # Change the save directory for the renamed file
    new_filepath = os.path.join(save_directory, new_filename)
    
    # Read the file and process
    with open(filename, 'r') as file:
        content = file.read()
    
    # Save the content to the new file in the specified directory
    with open(new_filepath, 'w') as new_file:
        new_file.write(content)

    # Delete the old file
    os.remove(filename)
    
    print(f"Processed '{filename}' -> '{new_filepath}' and deleted the old file.")


def main():
    """
    Main function to execute the program.

    Prompts the user for their in-game name and game name, 
    finds the latest merged data file, and renames it accordingly.

    Author: Mauro van Hulst, Maikel Boezer
    """
    # Create a simple Tkinter dialog to get user input
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    player_name = simpledialog.askstring("Input", "Enter your in-game name:")
    game_name = simpledialog.askstring("Input", "Enter the game you are playing:")

    # Capitalize the first letter of each input
    if player_name:
        player_name = player_name.capitalize()
    if game_name:
        game_name = game_name.lower()  # Keep game name lowercase for consistency

    if player_name and game_name:
        path_merged = "data/merged"
        path_input = "data/input"
        path_gaze = "data/gaze"
        path_emotion = "data/emotion"
        latest_file_merged = get_latest_file(path_merged)
        latest_file_input = get_latest_file(path_input)
        latest_file_gaze = get_latest_file(path_gaze)
        latest_file_emotion = get_latest_file(path_emotion)


        if latest_file_merged:
            process_file_merged(latest_file_merged, player_name, game_name, save_directory='data/merged')  # Pass the player name to process_file
        else:
            print("No merged data files found.")

        if latest_file_input:
            process_file(latest_file_input, player_name, game_name, save_directory='data/input')  # Pass the player name to process_file
        else:
            print("No input data files found.")

        if latest_file_gaze:
            process_file(latest_file_gaze, player_name, game_name, save_directory='data/gaze')  # Pass the player name to process_file
        else:
            print("No gaze data files found.")

        if latest_file_emotion:
            process_file(latest_file_emotion, player_name, game_name, save_directory='data/emotion')
        else:
            print("No emotion data files found.")        

    else:
        print("Name and game cannot be empty.")


if __name__ == "__main__":
    main()

def upload_newest_file(folder_path, dest_directory):
    """
    Finds the newest file in the folder and uploads it to the SFTP server.

    Args:
        folder_path (str): The folder to search for the newest file.

    @author: Maikel Boezer.
    """

    try:
        # Get all files in the directory
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        if not files:
            print("No files found for upload.")
            return

        # Find the newest file by creation time
        newest_file = max(files, key=os.path.getctime)
        print(f"Newest file to upload: {newest_file}")

        # Upload the newest file
        upload_file_to_sftp(
            local_file_path=newest_file,
            dest_directory=dest_directory,
        )
        print(f"File {newest_file} uploaded successfully.")
    except Exception as e:
        print(f"Error while uploading the newest file: {e}")

# Wait for 5 seconds after saving data
time.sleep(5)
upload_newest_file(folder_path='data/emotion/', dest_directory = "/data/emotion/")
upload_newest_file(folder_path='data/input/', dest_directory = "/data/input/")
upload_newest_file(folder_path='data/gaze/', dest_directory = "/data/gaze/")
upload_newest_file(folder_path='data/merged/', dest_directory = "/data/merged/")
upload_newest_file(folder_path='data/video/', dest_directory = "/data/video/")

