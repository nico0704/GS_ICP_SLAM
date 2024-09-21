# This class controls an Intel RealSense camera (D400-series) to capture color and depth images, 
# with the option to save them in a specified directory.
# It automatically retrieves calibration parameters when initializing.
# The camera's calibration parameters are retrieved and saved to a file optionally.

import numpy as np
import cv2
import os
import pyrealsense2 as rs
from datetime import datetime

# https://github.com/IntelRealSense/librealsense/tree/master/wrappers/python/examples
# https://github.com/IntelRealSense/librealsense/issues/3473

align_to = rs.stream.color
align = rs.align(align_to)

class Camera:
    def __init__(self, stop_after=2000, save_images=False, save_dir="dataset/custom_{}".format(datetime.now().strftime("%d%m%Y_%H_%M"))):
        self.cap = 0
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.depth_trunc = 3.0
        self.config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
        print("Trying to starting realsense pipeline.")
        try:
            self.pipeline.start(self.config)
        except Exception as e:
            print(e)
        print("Successfully started pipeline.")
        self.set_calib_parameters()
        self.stop_after = stop_after
        self.save_images = save_images
        self.save_dir = save_dir
        self.config_dir = "configs/calibration_{}".format(datetime.now().strftime("%d%m%Y_%H_%M"))
        if self.save_images:
            os.makedirs(self.save_dir, exist_ok=True)
            os.makedirs(os.path.join(self.save_dir, "rgb"), exist_ok=True)
            os.makedirs(os.path.join(self.save_dir, "depth"), exist_ok=True)
            os.makedirs(self.config_dir, exist_ok=True)
            self.write_cam_info()
        
    def set_calib_parameters(self):
        profile = self.pipeline.get_active_profile()
        depth_sensor = profile.get_device().first_depth_sensor()
        self.depth_scale = depth_sensor.get_depth_scale()
        depth_stream = profile.get_stream(rs.stream.depth)
        depth_intrinsics = depth_stream.as_video_stream_profile().get_intrinsics()
        self.W = depth_intrinsics.width
        self.H = depth_intrinsics.height
        self.fx = depth_intrinsics.fx
        self.fy = depth_intrinsics.fy
        self.cx = depth_intrinsics.ppx
        self.cy = depth_intrinsics.ppy
        self.depth_scale = 65.365
        print(f"Width: {self.W}, Height: {self.H}, fx: {self.fx}, fy: {self.fy}, cx: {self.cx}, cy: {self.cy}, Depth Scale: {self.depth_scale}")  
    
    def get_calib_parameters(self):
        return [self.W, self.H, self.fx, self.fy, self.cx, self.cy, self.depth_scale, self.depth_trunc, "custom"]
    
    def write_cam_info(self):
        print(f"Writing cam info to {os.path.join(self.config_dir, 'caminfo.txt')}")
        cam_info_path = os.path.join(self.config_dir, 'caminfo.txt')
        with open(cam_info_path, 'w') as cam_info:
            cam_info.write("## camera parameters\n")
            cam_info.write("W H fx fy cx cy depth_scale depth_trunc dataset_type\n")
            cam_info.write(f"{self.W} {self.H} {self.fx} {self.fy} {self.cx} {self.cy} {self.depth_scale} {self.depth_trunc} custom\n") 

    def get_images(self):
        if self.cap >= self.stop_after:
            return None, None
        
        print(f"Taking Frame {self.cap}.")
        frames = self.pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()
        
        if not depth_frame or not color_frame:
            print(f"Error: Failed to capture frame.")
            return None, None
        
        depth_image = np.asanyarray(depth_frame.get_data())
        depth_image = cv2.convertScaleAbs(depth_image, alpha=0.03)
        color_image = np.asanyarray(color_frame.get_data()).astype(np.float32)
        
        if self.save_images:
            rgb_dir_path = os.path.join(self.save_dir, "rgb")
            depth_dir_path = os.path.join(self.save_dir, "depth")
            cv2.imwrite(f"{rgb_dir_path}/frame{self.cap:06d}.jpg", color_image)
            cv2.imwrite(f"{depth_dir_path}/depth{self.cap:06d}.png", depth_image) 
        self.cap += 1
        return color_image, depth_image

    def stop(self):
        self.pipeline.stop()
