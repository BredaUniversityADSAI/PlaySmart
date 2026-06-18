import keyboard
import subprocess
import time
import psutil

def kill_openface():
    """Kill any leftover OpenFace FeatureExtraction.exe processes"""
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and 'FeatureExtraction.exe' in proc.info['name']:
            print(f"Killing leftover OpenFace process: PID {proc.pid}")
            proc.kill()

def main():
    """
    Handles script execution flow based on key presses (F7 to start, F12 to stop).
    Author: Thomas Pichardo, Mauro van Hulst, Maikel Boezer
    Modified: Pop-up (input only) shown on F7 before logging; data renamed and
    uploaded on F12 via pop_up_screen.py upload mode.
    """
    while True:
        print("Waiting for F7 or F12... (Press F7 to start or F12 to stop)")
        keyboard.wait('f7')

        print("F7 pressed, showing pop-up for player input...")
        kill_openface()  # Optional: clear leftover OpenFace processes
        processes = []
        try:
            # Show pop-up FIRST (input only, no file ops) so the user enters
            # their in-game name before any logging scripts run
            result = subprocess.run(["poetry", "run", "python", "src/pop_up_screen.py", "input"])
            if result.returncode == 0:
                print(" Player input captured!")
            else:
                print(" Input failed - aborting session.")
                continue

            # Delay so the pop-up has fully closed and no residual keystrokes
            # (the in-game name) are captured before keyboard logging starts
            time.sleep(2)

            # Start gaze, emotion, and input logging scripts
            print("Starting logging scripts...")
            processes.append(subprocess.Popen(["poetry", "run", "python", "src/eye_tracking_script.py"]))
            processes.append(subprocess.Popen(["poetry", "run", "python", "src/Emotion_gaze_visualization.py"]))
            processes.append(subprocess.Popen(["poetry", "run", "python", "src/keyboard_recording.py"]))
            processes.append(subprocess.Popen(["poetry", "run", "python", "src/microphone_recording.py"]))

            time.sleep(2)
            processes.append(subprocess.Popen(["poetry", "run", "python", "src/nuanic_eda.py"]))

            print("Waiting for F12 to stop and upload data...")
            keyboard.wait('f12')

            print("F12 pressed, stopping processes...")
            for process in processes:
                if process.poll() is None:
                    process.terminate()

            time.sleep(2)

            print("Processing and uploading data via pop_up_screen.py...")
            result = subprocess.run(["poetry", "run", "python", "src/pop_up_screen.py", "upload"])
            if result.returncode == 0:
                print(" Upload successful!")
            else:
                print(" Upload failed.")
        finally:
            for process in processes:
                if process.poll() is None:
                    process.terminate()
            print("Processes stopped.")

if __name__ == "__main__":
    main()