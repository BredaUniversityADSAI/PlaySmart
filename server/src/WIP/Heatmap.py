import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load the merged dataset (containing the gaze_x, gaze_y data)
merged_data = pd.read_csv("C://Users//mani1//Documents//GitHub//2024-25ab-fai3-specialisation-project-team-esports-1//data//merged_data_2024-09-30_15-32-38.csv")

# Load the gameplay image (replace 'image.png' with your actual image path)
image_path = 'image.png'  # Example path to the image
image = cv2.imread(image_path)

# Check if the image is loaded correctly
if image is None:
    print("Error: Could not load the image.")
    exit()

# Get image dimensions
screen_height, screen_width, _ = image.shape

# Create an empty heatmap matrix for the gaze points (based on image resolution)
heatmap = np.zeros((screen_height, screen_width), dtype=np.float32)

# Function to draw a circle around each gaze point to create a "spread" effect
def add_gaze_point_to_heatmap(heatmap, gaze_x, gaze_y, radius=20):
    cv2.circle(heatmap, (gaze_x, gaze_y), radius, 1, -1)  # Draw a filled circle

# Iterate through the merged dataset and accumulate gaze points into the heatmap
for index, row in merged_data.iterrows():
    gaze_x = int(row['gaze_x'] * screen_width)
    gaze_y = int(row['gaze_y'] * screen_height)
    
    # Check that the gaze points are within bounds of the image
    if 0 <= gaze_x < screen_width and 0 <= gaze_y < screen_height:
        add_gaze_point_to_heatmap(heatmap, gaze_x, gaze_y, radius=20)  # Increase radius if needed

# Normalize the heatmap for display purposes
heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)

# Create a color heatmap using OpenCV's colormap function
heatmap_color = cv2.applyColorMap(np.uint8(heatmap), cv2.COLORMAP_JET)

# Optionally, visualize the heatmap alone using matplotlib (to debug if heatmap is being created correctly)
plt.imshow(heatmap_color)
plt.title('Heatmap alone')
plt.show()

# Overlay the heatmap onto the image
overlay = cv2.addWeighted(image, 0.7, heatmap_color, 0.3, 0)

# Display the image with the heatmap overlay
cv2.imshow('Eye Tracking Heatmap Overlay', overlay)

# Wait indefinitely until a key is pressed
cv2.waitKey(0)

# Optionally, save the result to a file
output_image_path = 'heatmap_overlay_image.png'
cv2.imwrite(output_image_path, overlay)
print(f"Heatmap overlay image saved to: {output_image_path}")

# Close all windows
cv2.destroyAllWindows()