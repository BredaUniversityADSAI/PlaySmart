import pygame
import numpy as np
import keyboard
import torch
from ultralytics import YOLO
import screeninfo
import mss
import cv2

# Initialize YOLO model
model = YOLO("models/yolov8n.pt")  # Replace with your YOLO model (e.g., yolov5, yolov4)

# Set up device (GPU if available, else CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Initialize pygame
pygame.init()
clock = pygame.time.Clock()  # Create clock for FPS control

# Get screen resolution dynamically using screeninfo
screen = screeninfo.get_monitors()[0]
screen_width, screen_height = screen.width, screen.height

# Set up the Pygame window in full screen
window = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME | pygame.FULLSCREEN)
pygame.display.set_caption("Live Detection")

# Setup for screen capture using mss
with mss.mss() as sct:
    monitor = {"top": 0, "left": 0, "width": screen_width, "height": screen_height}

    # Loop for real-time detection
    while True:
        # Capture screen content using mss
        screenshot = np.array(sct.grab(monitor))

        # Convert the screenshot from RGBA to RGB (OpenCV uses BGR by default)
        screenshot_rgb = cv2.cvtColor(screenshot, cv2.COLOR_RGBA2RGB)

        # Flip the image upside down to match Pygame's coordinate system
        screenshot_rgb = np.flipud(screenshot_rgb)

        # Pre-process the frame (resize for faster detection)
        frame_resized = cv2.resize(screenshot_rgb, (640, 360))  # Resize to improve speed

        # Perform YOLO object detection on the resized frame
        results = model.predict(frame_resized, conf=0.5, device=device)

        # Process detection results
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Get box coordinates
                confidence = box.conf[0]  # Get detection confidence
                label = result.names[int(box.cls[0])]  # Get label for the detected object

                # Draw bounding box and label
                cv2.rectangle(frame_resized, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green box
                cv2.putText(frame_resized, f"{label} {confidence:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Convert the frame back to Pygame-friendly format
        frame_resized = np.flipud(frame_resized)  # Flip the frame upside down to match Pygame coordinates
        frame_surface = pygame.surfarray.make_surface(frame_resized)

        # Display the frame with detection results in Pygame window
        window.blit(frame_surface, (0, 0))
        pygame.display.update()

        # Event handling (to close the window)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Hotkey to stop the program
        if keyboard.is_pressed('f12'):
            break

        # Control the frame rate
        clock.tick(60)  # 60 frames per second (FPS)


# Clean up
pygame.quit()
