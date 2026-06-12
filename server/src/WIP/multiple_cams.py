import cv2
import pyvirtualcam

# Open the default camera (0)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Get the width and height of the video
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Start the virtual camera
with pyvirtualcam.Camera(width, height, 20) as virtual_cam:
    print(f'Using virtual camera: {virtual_cam.device}')

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Flip the frame (optional)
        frame = cv2.flip(frame, 1)

        # Send the frame to the virtual camera
        virtual_cam.send(frame)
        virtual_cam.sleep_until_next_frame()

        # Show the frame in a window (for testing)
        cv2.imshow('Virtual Webcam Feed', frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release the camera and close windows
cap.release()
cv2.destroyAllWindows()