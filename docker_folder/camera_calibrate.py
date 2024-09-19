import os
import pyrealsense2 as rs
from datetime import datetime

output_dir = "configs/custom_{}".format(datetime.now().strftime("%d%m%Y_%H_%M"))
os.makedirs(output_dir, exist_ok=True)

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

profile = pipeline.get_active_profile()
auto_device = profile.get_device()
auto_device = auto_device.as_auto_calibrated_device()
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
depth_stream = profile.get_stream(rs.stream.depth)
intrinsics = depth_stream.as_video_stream_profile().get_intrinsics()
W = intrinsics.width
H = intrinsics.height
fx = intrinsics.fx
fy = intrinsics.fy
cx = intrinsics.ppx
cy = intrinsics.ppy
depth_trunc = 8.0
depth_scale = 65.365
print(f"Width: {W}, Height: {H}, fx: {fx}, fy: {fy}, cx: {cx}, cy: {cy}, Depth Scale: {depth_scale}, Depth Trunc: {depth_trunc}")

## write calibration file ##
log_file_path = os.path.join(output_dir, 'caminfo.txt')
with open(log_file_path, 'w') as log_file:
    log_file.write("## camera parameters\n")
    log_file.write("W H fx fy cx cy depth_scale depth_trunc dataset_type\n")
    log_file.write(f"{W} {H} {fx} {fy} {cx} {cy} {depth_scale} {depth_trunc} custom\n")
