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
    Modified: Removes merging step, uploads data using pop_up_screen.py.
    """
    while True:
        print("Waiting for F7 or F12... (Press F7 to start or F12 to stop)")
        keyboard.wait('f7')

        print("F7 pressed, starting scripts...")
        kill_openface()  # Optional: clear leftover OpenFace processes
        processes = []
        try:
            # Start gaze, emotion, and input logging scripts
            processes.append(subprocess.Popen(["poetry", "run", "python", "src/eye_tracking_script.py"]))
            processes.append(subprocess.Popen(["poetry", "run", "python", "src/Emotion_gaze_visualization.py"]))
            processes.append(subprocess.Popen(["poetry", "run", "python", "src/keyboard_recording.py"]))

            print("Waiting for F12 to stop and upload data...")
            keyboard.wait('f12')

            print("F12 pressed, stopping processes...")
            for process in processes:
                if process.poll() is None:
                    process.terminate()

            time.sleep(2)

            print("Uploading latest data files via pop_up_screen.py...")
            result = subprocess.run(["poetry", "run", "python", "src/pop_up_screen.py"])
            if result.returncode == 0:
                print(" Upload successful and pop-up shown!")
            else:
                print(" Upload failed.")
        finally:
            for process in processes:
                if process.poll() is None:
                    process.terminate()
            print("Processes stopped.")

if __name__ == "__main__":
    main()

