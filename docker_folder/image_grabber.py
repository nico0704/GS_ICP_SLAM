import cv2
import os
import time
import numpy as np
import pyrealsense2 as rs
from datetime import datetime
from datetime import date
import time

# Directory to save the images
output_dir = f'custom_{date.today().isoformat()}'

# Create the directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)
os.makedirs(f"{output_dir}/rgb", exist_ok=True)
os.makedirs(f"{output_dir}/depth", exist_ok=True)

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Start streaming with the chosen resolution and framerate
config.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start the pipeline
pipeline.start(config)

# Create an align object
# rs.stream.color is the stream type we want to align depth frames to
align_to = rs.stream.color
align = rs.align(align_to)

i = 0
index = 0
try:
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()

        # Align the depth frame to the color frame
        aligned_frames = align.process(frames)

        # Get aligned frames
        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not depth_frame or not color_frame:
            print(f"Error: Failed to capture frame {i}.")
            break

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Get the current timestamp
        timestamp = time.time()

        print(f"Taking Frame {i}")

        # Save the RGB image
        color_image_filename = f'{i}_color.png'
        color_image_path = os.path.join(output_dir, f'rgb/frame{index:06}.jpg')
        cv2.imwrite(color_image_path, color_image)

        # Save the depth image (scaling to 8-bit for visualization)
        depth_image_path = os.path.join(output_dir, f'depth/depth{index:06}.png')
        depth_image_8bit = cv2.convertScaleAbs(depth_image, alpha=0.2)
        
        cv2.imwrite(depth_image_path, depth_image_8bit)

        i += 1
        index += 1

        time.sleep(0.1)

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting on user command.")
            break

finally:
    # Stop the pipeline
    pipeline.stop()

    # Close any OpenCV windows
    cv2.destroyAllWindows()
