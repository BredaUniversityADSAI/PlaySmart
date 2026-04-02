# Toolkit Setup Guide

## Prerequisites
Before getting started, make sure you have the following installed and available on your system:

- Python (3.9 or 3.10 is recommended)
- Poetry (dependency manager)
- A connected webcam
- A connected Tobii eye tracker 

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

## Starting the Toolkit
1. Ensure your webcam and eye tracker are connected before launching.
2. Run the toolkit by executing the main.bat file:

 `main.bat` Or double-click it in File Explorer.

---

## Controls

| Key | Action |
|-----|--------|
| `F7` | Start recording |
| `F12` | Stop recording |

---

## Troubleshooting

> [!TIP]
> Always make sure your devices are connected *before* launching the toolkit.

> [!NOTE]
> If Poetry is not found after installation, restart your terminal and verify that Poetry is added to your system `PATH`.

> [!WARNING]
> If `poetry install` fails, confirm you are in the correct folder — it must contain `pyproject.toml`.

---

## Project Structure *(optional — fill in as needed)*
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






