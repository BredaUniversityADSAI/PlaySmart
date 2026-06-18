import os
import glob
import datetime
import tkinter as tk
from tkinter import simpledialog, ttk
import json
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server.python_app.sftp_upload import upload_file_to_sftp


# ------------------ Utility Functions ------------------

def get_latest_file(path):
    files = glob.glob(os.path.join(path, "*.csv"))
    return max(files, key=os.path.getmtime) if files else None


def get_latest_by_extension(path, extension):
    files = glob.glob(os.path.join(path, f"*.{extension}"))
    return max(files, key=os.path.getmtime) if files else None


def get_latest_video_any(path):
    files = glob.glob(os.path.join(path, "*.mp4")) + glob.glob(os.path.join(path, "*.mkv"))
    return max(files, key=os.path.getmtime) if files else None


def get_next_player_id(mapping):
    existing_ids = [v for v in mapping.values() if v.startswith('P')]
    nums = [int(pid[1:]) for pid in existing_ids if pid[1:].isdigit()]
    return f'P{max(nums, default=0) + 1:03d}'


def load_mapping(mapping_file='data/json/ign_mapping.json'):
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r') as file:
            return json.load(file)
    return {}


def save_mapping(mapping, mapping_file='data/json/ign_mapping.json'):
    os.makedirs(os.path.dirname(mapping_file), exist_ok=True)
    with open(mapping_file, 'w') as file:
        json.dump(mapping, file, indent=4)


def load_daily_game_count(count_file='data/json/date_game_count.json'):
    if os.path.exists(count_file):
        try:
            with open(count_file, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}
    return {}


def save_daily_game_count(data, count_file='data/json/date_game_count.json'):
    os.makedirs(os.path.dirname(count_file), exist_ok=True)
    with open(count_file, 'w') as file:
        json.dump(data, file, indent=4)


def update_daily_game_count(game_name):
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    data = load_daily_game_count()

    data.setdefault(today, {})
    data[today][game_name] = data[today].get(game_name, 0) + 1

    save_daily_game_count(data)
    return get_ordinal(data[today][game_name]), today


def get_ordinal(n):
    return f"{n}{'th' if 4 <= n % 100 <= 20 else {1:'st',2:'nd',3:'rd'}.get(n%10,'th')}"


def upload_newest_file(folder_path, dest_directory):
    if not os.path.exists(folder_path):
        print(f"Missing folder: {folder_path}")
        return

    files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]

    if not files:
        print(f"No files in {folder_path}")
        return

    newest = max(files, key=os.path.getctime)

    for i in range(3):
        try:
            print(f"Uploading: {newest}")
            upload_file_to_sftp(newest, dest_directory)
            return
        except Exception as e:
            print(f"Retry {i+1} failed: {e}")
            time.sleep(2)


# ------------------ Session Context ------------------

SESSION_CONTEXT_FILE = 'data/json/session_context.json'


def save_session_context(context, context_file=SESSION_CONTEXT_FILE):
    os.makedirs(os.path.dirname(context_file), exist_ok=True)
    with open(context_file, 'w') as file:
        json.dump(context, file, indent=4)


def load_session_context(context_file=SESSION_CONTEXT_FILE):
    if os.path.exists(context_file):
        with open(context_file, 'r') as file:
            return json.load(file)
    return None


def clear_session_context(context_file=SESSION_CONTEXT_FILE):
    if os.path.exists(context_file):
        os.remove(context_file)


# ------------------ Mode: Collect Input (F7) ------------------

def collect_input():
    """Show the pop-up, gather name/game, and persist to session_context.json.
    Does NOT touch or upload any files."""

    class DualInputDialog(simpledialog.Dialog):
        def body(self, master):
            tk.Label(master, text="In-game name:").grid(row=0, column=0)
            tk.Label(master, text="Game:").grid(row=1, column=0)

            mapping = load_mapping()

            self.player = ttk.Combobox(master, values=sorted(mapping.keys()))
            self.player.grid(row=0, column=1)

            self.game = ttk.Combobox(master, values=["valorant", "league_of_legends", "other"], state="readonly")
            self.game.set("valorant")
            self.game.grid(row=1, column=1)

            return self.player

        def apply(self):
            self.player_name = self.player.get().strip()
            self.game_name = self.game.get().strip().lower()

    root = tk.Tk()
    root.withdraw()

    dialog = DualInputDialog(root)
    player_name = getattr(dialog, 'player_name', None)
    game_name = getattr(dialog, 'game_name', None)

    if not player_name or not game_name:
        print("Invalid input")
        return 1

    save_session_context({
        "player_name": player_name,
        "game_name": game_name,
        "timestamp": datetime.datetime.now().isoformat(),
    })
    print("Session context saved.")
    return 0


# ------------------ Mode: Process & Upload (F12) ------------------

def process_and_upload():
    """Read the stored session context, rename the session's files, and upload.
    No pop-up is shown."""

    context = load_session_context()
    if not context:
        print("No session context found. Did the F7 pop-up run?")
        return 1

    player_name = context.get("player_name")
    game_name = context.get("game_name")

    if not player_name or not game_name:
        print("Invalid session context")
        return 1

    # ---------------- PLAYER ----------------
    mapping = load_mapping()

    if player_name not in mapping:
        mapping[player_name] = get_next_player_id(mapping)
        save_mapping(mapping)

    player_id = mapping[player_name]

    ordinal, today = update_daily_game_count(game_name)
    now = datetime.datetime.now().strftime("%H-%M-%S")

    base_name = f"{ordinal}_game_{player_id}_{game_name}_{today}_{now}"

    def is_already_processed(filepath):
        return "_game_" in os.path.basename(filepath)

    # ---------------- CSV ----------------
    for folder, tag in {
        "data/input": "input",
        "data/gaze": "gaze",
        "data/emotion": "emotion",
        "data/eda": "eda",
    }.items():

        latest = get_latest_file(folder)

        if latest and not is_already_processed(latest):
            new_path = os.path.join(folder, f"{base_name}_{tag}.csv")
            os.replace(latest, new_path)
            print(f"Renamed {tag}")

    # ---------------- AUDIO ----------------
    audio_folder = "data/audio"

    latest_audio = get_latest_by_extension(audio_folder, "wav")

    if latest_audio:
        new_audio = os.path.join(audio_folder, f"{base_name}.wav")
        os.replace(latest_audio, new_audio)

        txt = latest_audio.replace(".wav", ".txt")
        if os.path.exists(txt):
            os.replace(txt, os.path.join(audio_folder, f"{base_name}.txt"))

    # ---------------- VIDEO ----------------
    video_src = os.path.join(os.path.expanduser("~"), "Videos")
    video_dst = os.path.join(os.path.expanduser("~"), "Documents", "research_software", "data", "video")
    os.makedirs(video_dst, exist_ok=True)

    latest_video = get_latest_video_any(video_src)

    if latest_video:
        ext = os.path.splitext(latest_video)[1]
        os.replace(latest_video, os.path.join(video_dst, f"{base_name}{ext}"))

    # ---------------- UPLOAD ----------------
    time.sleep(3)

    upload_newest_file('data/emotion', "/data/emotion/")
    upload_newest_file('data/input', "/data/input/")
    upload_newest_file('data/gaze', "/data/gaze/")
    upload_newest_file(video_dst, "/data/video/")
    upload_newest_file('data/eda', "/data/eda/")

    # upload all audio
    if os.path.exists(audio_folder):
        for f in os.listdir(audio_folder):
            full = os.path.join(audio_folder, f)
            if os.path.isfile(full):
                upload_file_to_sftp(full, "/data/audio/")

    # Clean up so stale context isn't reused next session
    clear_session_context()
    return 0


def main():
    # Default to "input" mode if no argument is given
    mode = sys.argv[1] if len(sys.argv) > 1 else "input"

    if mode == "input":
        sys.exit(collect_input())
    elif mode == "upload":
        sys.exit(process_and_upload())
    else:
        print(f"Unknown mode: {mode}. Use 'input' or 'upload'.")
        sys.exit(1)


if __name__ == "__main__":
    main()