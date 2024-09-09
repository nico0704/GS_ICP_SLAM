import cv2
import numpy as np
import os
from datetime import date
import pyrealsense2 as rs
import time

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Start streaming with the chosen resolution and framerate
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start the pipeline
pipeline.start(config)

# Definiere die Anzahl der inneren Ecken im Schachbrettmuster
chessboard_size = (9, 6)
frame_size = (640, 480)

# Vorbereiten von Objektpunkten, z.B. (0,0,0), (1,0,0), (2,0,0), ....,(8,5,0)
objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)

# Arrays um Objektpunkte und Bildpunkte von allen Bildern zu speichern
objpoints = []  # 3D Punkte in realer Welt
imgpoints = []  # 2D Punkte in Bildebene

images = []
for i in range(12):
    print(f"taking frame {i}")
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()
    if not color_frame:
        print(f"Error: Failed to capture frame {i}.")
        break
    images.append(np.asanyarray(color_frame.get_data()))
    time.sleep(0.1)

# Lade Bilder zur Kalibrierung
for img in images:
    H, W = img.shape[:2]
    # cv2.imwrite("img.jpg", img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Finden der Schachbrett-Ecken
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

    # Wenn gefunden, dann füge Objektpunkte und Bildpunkte hinzu
    if ret:
        objpoints.append(objp)
        imgpoints.append(corners)

# Kamera Kalibrierung
ret, camera_matrix, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, frame_size, None, None)

# Ausgabe der intrinsischen Parameter
print("Camera matrix:")
print(camera_matrix)

# fx, fy, cx, cy können direkt aus der camera_matrix extrahiert werden

fx = camera_matrix[0, 0]
fy = camera_matrix[1, 1]
cx = camera_matrix[0, 2]
cy = camera_matrix[1, 2]

print(f"fx={fx}, fy={fy}, cx={cx}, cy={cy}")

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

# Holen der Tiefenskala
depth_sensor = pipeline.get_active_profile().get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
print("Depth Scale is: ", depth_scale)

pipeline.stop()

output_dir = f'../configs/custom_{date.today().isoformat()}'
os.makedirs(output_dir, exist_ok=True)

# write calibration file
log_file_path = os.path.join(output_dir, 'caminfo.txt')
with open(log_file_path, 'a') as log_file:
    log_file.write("## camera parameters\n")
    log_file.write("W H fx fy cx cy depth_scale depth_trunc dataset_type\n")
    log_file.write(f"{W} {H} {fx} {fy} {cx} {cy} {depth_scale} 3.0 custom\n")