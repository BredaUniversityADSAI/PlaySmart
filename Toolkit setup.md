# Toolkit Setup Guide

## Prerequisites

Before getting started, make sure you have the following installed and available on your system:

- Python (3.9 or [3.10](https://www.python.org/downloads/release/python-3100/) is recommended)
- Poetry (dependency manager) - pip install poetry
- OBS [Installer](https://obsproject.com/download)
  - For setting up refer to OBS installer [readme](obs%20settings/readme.md)
- Tobii Eye Tracker Manager Pro [Installer](https://www.tobii.com/products/software/applications-and-developer-kits/tobii-pro-eye-tracker-manager#downloads%22)
- A connected webcam
- A connected Tobii eye tracker
- ffmpeg

### Installing ffmpeg
ffmpeg is required by the Whisper speech-to-text model to decode audio files. Without it, transcription will fail with a `FileNotFoundError`.

The easiest way to install it on Windows is via winget:

```bash
winget install ffmpeg
```

Alternatively, download it manually from [ffmpeg.org](https://ffmpeg.org/download.html), extract the archive, and add the `bin` folder to your system `PATH` environment variable.

After installing, verify it works by running:

```bash
ffmpeg -version
```

If this prints version info, ffmpeg is correctly installed and on your PATH.

> [!NOTE]
> If ffmpeg is not found after installation, restart your terminal so the updated PATH is picked up.

## Setting Up the Poetry Environment

1. Verify that Poetry is installed by running:

```bash
poetry --version
```

If this command is not found, follow the Poetry installation guide.

2. Open a terminal and navigate to the project folder containing the `pyproject.toml` and `poetry.lock` files:

```bash
cd path/to/project
```

3. Install the project dependencies:

```bash
poetry install
```

This will create a `.venv` virtual environment folder inside the project directory.

## Adding OpenFace to the project folder

A planned future improvement will remove the need for OpenFace, but for now it is still required. The version used for this project is **2.2.0**.

There are three ways to add it to the project folder:

1. Copy it from a nearby machine where the Toolkit is already deployed using a USB stick.

2. Send it to yourself via Discord or MS Teams.

3. Download it from [PlaySmart google account google drive](https://drive.google.com/drive/u/1/my-drive).

Once obtained, unzip OpenFace and place the folder inside the project directory.

## Starting the Toolkit

1. Ensure your webcam and eye tracker are connected before launching.
2. Tobii Eye Tracker Manager Pro and OBS are running with correct settings
3. Run the toolkit by executing the main.bat file:

 `main.bat` Or double-click it in File Explorer.

---

## Controls

| Key     | Action          |
| ------- | --------------- |
| `F7`    | Start recording |
| `F12`   | Stop recording  |

---

## Installing the Benchmark

MSI Afterburner version 4.6.6 is used to benchmark the PCs and verify that they can run the Toolkit alongside the game without performance issues.

1. First, install MSI Afterburner.

   - The installer can be downloaded from the [website](https://www.msi.com/Landing/afterburner/graphics-cards).
   - The installer can also be downloaded from the PlaySmart [Google Drive](https://drive.google.com/drive/u/1/my-drive).

2. Install it **without** Norton 360 for Gamers.

3. Do install it **with** RivaTuner Statistics Server.

4. After installing, go to Settings and then the Benchmark tab. Add hotkeys to start and stop the benchmark - recommended are `F8` to start and `F9` to stop.

5. Make sure the `benchmark.txt` is saved to a location that is easy to find.

The benchmark can be compared to the reference benchmarks taken at The Hive, which were recorded both with and without the Toolkit running during a deathmatch in Valorant.

Benchmark without the toolkit:

```
VALORANT-Win64-Shipping.exe benchmark completed, 99601 frames rendered in 435.484 s
                     Average framerate  :  228.7 FPS
                     Minimum framerate  :    0.0 FPS
                     Maximum framerate  :  362.2 FPS
                     1% low framerate   :    0.0 FPS
                     0.1% low framerate :    0.0 FPS
```
Benchmark with the toolkit:

```
18-06-2026, 19:16:47 VALORANT-Win64-Shipping.exe benchmark completed, 76295 frames rendered in 392.203 s
                     Average framerate  :  194.5 FPS
                     Minimum framerate  :    0.0 FPS
                     Maximum framerate  :  271.7 FPS
                     1% low framerate   :    0.0 FPS
                     0.1% low framerate :    0.0 FPS
```

---

## Troubleshooting

> [!TIP]
> Always make sure your devices are connected *before* launching the toolkit.

> [!NOTE]
> If Poetry is not found after installation, restart your terminal and verify that Poetry is added to your system `PATH`.

> [!WARNING]
> If `poetry install` fails, confirm you are in the correct folder - it must contain `pyproject.toml`.

---

## Project Structure

```
project/
├── .venv/            # Virtual environment (auto-generated)
├── data
│   ├── emotion
│   ├── gaze
│   ├── input
│   ├── json
│   └── video
├── obs settings
├── OpenFace_2.2.0_win_x64
├── src
│   ├── Emotion_gaze_visualization.py
│   ├── enemy_detection.py
│   ├── eye_tracking_script.py
│   ├── key_listener.py
│   ├── keyboard_recording.py
│   ├── nuanic_rings.py
│   ├── pop_up_screen.py
│   ├── sftp_upload.py
│   ├── tobii_research.py
│   └── models
|       └── yolov8n.pt
├── main.bat          # Entry point to launch the toolkit
├── poetry.lock       # Locked dependency versions
└── pyproject.toml    # Poetry project configuration
```
