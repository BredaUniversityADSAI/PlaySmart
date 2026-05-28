import keyboard
import subprocess
import time

def main():
    while True:
        print("Waiting for F7 or F12... (Press F7 to start or F12 to stop)")
        keyboard.wait('f7')
        
        print("F7 pressed, starting scripts...")
        processes = []
        try:
            processes.append(subprocess.Popen(["poetry", "run", "python", "src/eye_tracking_script.py"], stderr=subprocess.DEVNULL))

            processes.append(subprocess.Popen(["poetry", "run", "python", "src/Emotion_gaze_visualization.py"]))

            # Wait before starting keyboard recording
            time.sleep(5)
            processes.append(subprocess.Popen(["poetry", "run", "python", "src/keyboard_recording.py"]))

            # Wait for F12 to trigger the merging process
            print("Waiting for F12 to start merging datasets...")
            keyboard.wait('f12')

            print("F12 pressed, merging datasets...")
            merge_result = subprocess.run(["poetry", "run", "python", "src/merge_datasets.py"])
            if merge_result.returncode == 0:
                print("Merge successful, showing Pop-up screen...")
                subprocess.run(["poetry", "run", "python", "src/pop_up_screen.py"])
            else:
                print("Merge failed, not showing Pop-up screen.")
        finally:
            # Stop all subprocesses when F12 is pressed
            for process in processes:
                if process.poll() is None:  # Check if process is still running
                    process.terminate()
            print("Processes stopped. Ready for next F7 press.")

if __name__ == "__main__":
    main()
