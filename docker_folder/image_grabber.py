import cv2
import os
import time
import numpy as np
import pyrealsense2 as rs
from datetime import datetime
import time

output_dir = "dataset/custom_{}".format(datetime.now().strftime("%d%m%Y_%H_%M"))

os.makedirs(output_dir, exist_ok=True)
os.makedirs(f"{output_dir}/rgb", exist_ok=True)
os.makedirs(f"{output_dir}/depth", exist_ok=True)

pipeline = rs.pipeline()
config = rs.config()

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

pipeline.start(config)

align_to = rs.stream.color
align = rs.align(align_to)

index = 0
try:
    while True:
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)

        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not depth_frame or not color_frame:
            print(f"Error: Failed to capture frame {index}.")
            break

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        timestamp = time.time()

        print(f"Taking Frame {index}")

        color_image_path = os.path.join(output_dir, f'rgb/frame{index:06}.jpg')
        cv2.imwrite(color_image_path, color_image)
        depth_image_path = os.path.join(output_dir, f'depth/depth{index:06}.png')
        depth_image = cv2.convertScaleAbs(depth_image, alpha=0.03)
        cv2.imwrite(depth_image_path, depth_image)

        index += 1
        time.sleep(0.1)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting on user command.")
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()