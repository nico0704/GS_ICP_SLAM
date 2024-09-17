import numpy as np
import open3d as o3d
import cv2
import os
import pyrealsense2 as rs
from datetime import date

# TODO: ALIGN IMAGES!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Create an align object
# rs.stream.color is the stream type we want to align depth frames to
align_to = rs.stream.color
align = rs.align(align_to)

class Camera:
    def __init__(self):
        self.cap = 0
        self.stop_after = 2000 # will stop after taking 2000 frames
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.depth_trunc = 8.0
        self.output_dir = f"custom_{date.today().isoformat()}"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/rgb", exist_ok=True)
        os.makedirs(f"{self.output_dir}/depth", exist_ok=True)
        self.config.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        print("Starting realsense pipeline...")
        try:
            self.pipeline.start(self.config)
        except Exception as e:
            print(e)
        self.set_calib_parameters()
        
    def set_calib_parameters(self):
        profile = self.pipeline.get_active_profile()
        depth_sensor = profile.get_device().first_depth_sensor()
        self.depth_scale = depth_sensor.get_depth_scale()
        depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
        color_stream = profile.get_stream(rs.stream.color)  # Color stream
        depth_stream = profile.get_stream(rs.stream.depth)
        depth_intrinsics = depth_stream.as_video_stream_profile().get_intrinsics()
        color_intrinsics = color_stream.as_video_stream_profile().get_intrinsics()
        self.W = color_intrinsics.width
        self.H = color_intrinsics.height
        self.fx = color_intrinsics.fx
        self.fy = color_intrinsics.fy
        self.cx = color_intrinsics.ppx
        self.cy = color_intrinsics.ppy
        self.depth_scale = 65.365
        print(f"Width: {self.W}, Height: {self.H}, fx: {self.fx}, fy: {self.fy}, cx: {self.cx}, cy: {self.cy}, Depth Scale: {self.depth_scale}")
        # return [self.W, self.H, self.fx, self.fy, self.cx, self.cy, self.depth_scale, self.depth_trunc, "custom"]     
    
    def get_calib_parameters(self):
        return [self.W, self.H, self.fx, self.fy, self.cx, self.cy, self.depth_scale, self.depth_trunc, "custom"]  

    def get_images(self):
        if self.cap == self.stop_after:
            return None, None
        frames = self.pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()
        if not depth_frame or not color_frame:
            print(f"Error: Failed to capture frame...")
            return None, None
        depth_image = np.asanyarray(depth_frame.get_data()).astype(np.float32)
        depth_image = cv2.convertScaleAbs(depth_image, alpha=0.03)
        color_image = np.asanyarray(color_frame.get_data()).astype(np.float32)
        print(f"Taking Frame {self.cap}")

        # cv2.imwrite("test.jpg", color_image)
        
        # rgb_image = cv2.imread(f"dataset/custom/rgb/frame{self.cap:06d}.jpg")
        # depth_image = np.array(o3d.io.read_image(f"dataset/custom/depth/depth{self.cap:06d}.png")).astype(np.float32)
        
        self.cap += 1
        return color_image, depth_image

    def stop(self):
        self.pipeline.stop()
