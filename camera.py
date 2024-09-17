import numpy as np
import open3d as o3d
import cv2
import os
import pyrealsense2 as rs
from datetime import date

class Camera:
    def __init__(self):
        self.cap = 0
        self.stop_after = 2000 # will stop after taking 2000 frames
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.depth_trunc = 3.0
        self.output_dir = f"custom_{date.today().isoformat()}"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/rgb", exist_ok=True)
        os.makedirs(f"{self.output_dir}/depth", exist_ok=True)
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        print("Starting realsense pipeline...")
        try:
            self.pipeline.start(self.config)
        except Exception as e:
            print(e)
        self.set_calib_parameters()
        
    def set_calib_parameters(self):
        profile = self.pipeline.get_profile()
        depth_sensor = profile.get_device().first_depth_sensor()
        self.depth_scale = depth_sensor.get_depth_scale()
        depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
        depth_intrinsics = depth_profile.get_intrinsics()
        self.W = depth_intrinsics.width
        self.H = depth_intrinsics.height
        self.fx = depth_intrinsics.fx
        self.fy = depth_intrinsics.fy
        self.cx = depth_intrinsics.ppx
        self.cy = depth_intrinsics.ppy
        print(f"Width: {self.W}, Height: {self.H}, fx: {self.fx}, fy: {self.fy}, cx: {self.cx}, cy: {self.cy}, Depth Scale: {self.depth_scale}")
        return (self.W, self.H, self.fx, self.fy, self.cx, self.cy, self.depth_scale, self.depth_trunc)     
    
    def get_calib_parameters(self):
        (self.W, self.H, self.fx, self.fy, self.cx, self.cy, self.depth_scale, self.depth_trunc)  

    def get_images(self):
        if self.cap == self.stop_after:
            return None, None
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            print(f"Error: Failed to capture frame...")
            return None, None
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        print(f"Taking Frame {self.cap}")
        
        # rgb_image = cv2.imread(f"dataset/custom/rgb/frame{self.cap:06d}.jpg")
        # depth_image = np.array(o3d.io.read_image(f"dataset/custom/depth/depth{self.cap:06d}.png")).astype(np.float32)
        
        self.cap += 1
        return color_image, depth_image

    def stop(self):
        self.pipeline.stop()
