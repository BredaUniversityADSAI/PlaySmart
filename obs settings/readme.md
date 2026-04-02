# OBS Input Overlay Setup Guide

> **Show your mouse and keyboard inputs live on screen while recording in OBS.**  
> Based on this [YouTube tutorial](https://www.youtube.com/watch?v=JNNqm3a2oZQ).

---

## Step 1 — Download the Plugin

1. The plugin can be found **[here](https://github.com/univrsal/input-overlay/releases/tag/v4.8)**
2. Assuming you're on **Windows**, download either the **32-bit** or **64-bit** version — it will be a `.zip` file.

---

## Step 2 — Install the Plugin

1. **Right-click** the downloaded `.zip` → **Extract All**.
2. Open the extracted folder and **Shift+select** both the `data` and `obs-plugin` folders.
3. Navigate to:
   ```
   C:\Program Files\OBS Studio\
   ```
4. **Replace** the existing `data` and `obs-plugins` folders with the ones you just downloaded.

---

## Step 3 — Set Up Your Overlays Folder

1. Right-click somewhere convenient → **New Folder**.
2. Name it something like `overlays`.
3. This folder will hold all the **images** for your mouse, keyboard, and controller overlays.

---

## Step 4 — Choose & Extract Your Presets

Navigate back to the downloaded presets folder. Pick what fits your use case:

| Use Case | Preset to Extract |
|---|---|
| Controller (gamepad) | `gamepad` |
| Mouse only | `mouse` |
| WASD keys only | `WD` (WASD preset) |
| Full keyboard | `Cordy` |

> **Tip:** You can mix and match — extract multiple presets if needed.

Once extracted, **drag everything into your new `overlays` folder**.

---

## Step 5 — Add the Source in OBS Studio

1. In OBS Studio, go to the **Sources** panel.
2. Click the **`+`** button → select **Input Overlay**.
3. Give it a name (e.g., `Mouse Overlay`).

### Configuring the Mouse Overlay

1. Click **Browse** and navigate to your mouse overlay folder.
2. Select the **images** folder first, then go back and grab the **config file**.
3. There are multiple config options — the option **mouse-no-movement** is recommended.
4. Hit **OK**.

---

## Step 6 — Position & Test

- **Drag** the overlay to wherever you want it to appear on screen during recording.
- Click around — you should see the overlay **react in real time** to your inputs! ✅

---

## Step 7 — Add keyboard overlay

Repeat **Step 5** for any additional overlays you want. 

For **Valorant** the WASD overlay is recommended.
For **League of Legends** the full keyboard overly is recommended

1. Click **`+`** → **Input Overlay**.
2. Name it (e.g., `WASD Overlay`).
3. Browse to the WASD images folder.
4. Pick the config file that looks best to you.
5. Position it on screen.

---
> [!NOTE]
> If the readme is unclear or it is not workon try following the YouTube tutorial [here](https://www.youtube.com/watch?v=JNNqm3a2oZQ)