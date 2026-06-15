import os
import glob
import time
from datetime import datetime
import pandas as pd

def get_latest_file(directory, prefix):
    """
    Get the latest CSV file in the specified directory with a given prefix.
    
    Parameters:
    - directory (str): The directory to search for files.
    - prefix (str): The prefix of the file (e.g., 'gaze_data_' or 'input_log_').
    
    Returns:
    - str: The path of the latest file that matches the prefix.
    - None: If no files are found with the specified prefix.

    Authors: Mauro van Hulst
    """
    print(f"Searching for the latest file with prefix '{prefix}' in the directory '{directory}'...")

    # Search for all CSV files in the directory with the specified prefix
    list_of_files = glob.glob(os.path.join(directory, f'{prefix}*.csv'))
    
    # If no files are found, return None
    if not list_of_files:
        return None
    
    # Sort the files by modification time and return the latest one
    latest_file = max(list_of_files, key=os.path.getmtime)
    return latest_file

def merge_datasets():
    """
    Merge the latest gaze data, input log, and webcam CSV files based on the 'unix_time' column.
    
    The function searches for the latest gaze, keyboard/mouse input log, and webcam log files, loads them as DataFrames,
    and merges them on the 'unix_time' column. It processes the gaze data by dropping rows with NaN values,
    rounding the gaze data to 3 decimal places, and averaging the left and right gaze data. Finally, the
    merged dataset is saved as a CSV file in the '../data/merged' directory.

    Returns:
    - None

     
    """
    # Short delay before starting the merging process (e.g., 1 second)
    time.sleep(1)
    
    # Define the folder where the CSV files are stored
    folder_name = 'data'
    
    # Find the latest gaze, input log, and webcam log files
    latest_gaze_file = get_latest_file(f"{folder_name}/gaze", 'gaze_data_')
    print(latest_gaze_file)
    latest_kbm_file = get_latest_file(f"{folder_name}/input", 'input_log_')
    print(latest_kbm_file)
    latest_webcam_file = get_latest_file(f"{folder_name}/emotion", 'emotion_data_')    
    print(latest_webcam_file)

    if latest_gaze_file is None or latest_kbm_file is None or latest_webcam_file is None:
        print("Error: Could not find one or more of the CSV files.")
        return
    
    print(f"Latest gaze data file: {latest_gaze_file}")
    print(f"Latest input log file: {latest_kbm_file}")
    print(f"Latest webcam data file: {latest_webcam_file}")

    # Load the CSV files
    df_gaze = pd.read_csv(latest_gaze_file)
    df_kbm = pd.read_csv(latest_kbm_file)
    df_webcam = pd.read_csv(latest_webcam_file)

    # Calculate the average gaze position
    if 'left_gaze_x' in df_gaze.columns and 'right_gaze_x' in df_gaze.columns:
        df_gaze['gaze_x'] = (df_gaze['left_gaze_x'] + df_gaze['right_gaze_x']) / 2
        df_gaze['gaze_y'] = (df_gaze['left_gaze_y'] + df_gaze['right_gaze_y']) / 2
    else:
        df_gaze['gaze_x'] = df_gaze['left_gaze_x']
        df_gaze['gaze_y'] = df_gaze['left_gaze_y']


    # Round the average gaze position columns to 3 decimal places
    df_gaze[['gaze_x', 'gaze_y']] = df_gaze[['gaze_x', 'gaze_y']].round(3)

    # Drop the individual gaze columns
    df_gaze.drop(columns=['left_gaze_x', 'left_gaze_y', 'right_gaze_x', 'right_gaze_y'], inplace=True)

    # Merge the gaze and input log datasets on the unix_time column, keeping all gaze data
    print("Merging the gaze and input log datasets...")
    df_merge_1 = pd.merge(df_gaze, df_kbm, on='unix_time', how='left')

    # Drop unnecessary columns and rename where needed
    df_merge_1.drop(columns=['timestamp_y', 'screen_resolution_y'], inplace=True)
    df_merge_1.rename(columns={'timestamp_x': 'timestamp', 'screen_resolution_x': 'screen_resolution'}, inplace=True)

    # Drop duplicates and rows with NaN gaze data
    df_merge_1.drop_duplicates(subset='timestamp', inplace=True)
    df_merge_1.dropna(subset=['gaze_x', 'gaze_y'], inplace=True)

    # Merge with the webcam data
    print("Merging the webcam dataset...")
    df_merge_2 = pd.merge(df_merge_1, df_webcam, on='unix_time', how='left')
    df_merge_2.drop(columns=['timestamp_y'], inplace=True)
    df_merge_2.rename(columns={'timestamp_x': 'timestamp'}, inplace=True)
    df_merge_2.dropna(subset=['timestamp'], inplace=True)
    df_merge_2.drop_duplicates(subset=['timestamp'], inplace=True)

    # Save the final merged dataframe to a CSV file
    merged_file_path = os.path.join('data/merged', 'merged_data_' + datetime.now().strftime('%d-%m-%Y_%H-%M-%S') + '.csv')
    df_merge_2.to_csv(merged_file_path, index=False)
    
    print(f'Merged data saved to: {merged_file_path}')


# Main execution starts here
if __name__ == "__main__":
    merge_datasets()