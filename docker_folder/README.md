# Running GS_ICP_SLAM with docker and custom data

## 1. Clone forked repository
```bash
git clone https://github.com/nico0704/GS_ICP_SLAM.git
```

## 2. Build docker image
```bash
cd GS_ICP_SLAM/docker_folder
docker build -t gs_icp_slam_image .
```

## 3. Run container
```bash
chmod +x run.sh
./run.sh
```

## 4. Access container
```bash
docker exec -it gs_icp_slam_container bash
```
- name of container is set in `run.sh`

## 5. Install submodules (fast_gicp, diff-gaussian-rasterization, simple-knn)
  ```bash
  cd /home/GS_ICP_SLAM/docker_folder
  chmod +x install_submodules.sh
  ./install_submodules.sh    
  ```

## 6. Run the algorithm
### With live data from a realsense depth camera
  - Connect your realsense depth camera
    ```bash
    python gs_icp_slam_live.py
    ```

### Or create your own custom dataset and config
  - Your custom dataset should have the following structure:
    ```bash
    custom_dataset/
    ├── rgb/
    │   ├── frame000000.jpg
    │   ├── frame000001.jpg
    │   └── ...
    ├── depth/
    │   ├── depth000000.png
    │   ├── depth000001.png
    │   └── ...
    ```

  - Don't forget to add your config inside `GS_ICP_SLAM/configs/custom/your_caminfo.txt`, which should look similar to this:
    ``` bash
    ## camera parameters
    H W fx fy cx cy depth_scale depth_trunc dataset_type
    0000 0000 0000 0000 0000 0000 0000 0000 custom
    ```
  
  - Take a look at our scripts for getting images and calibration data:
    - [image_grabber.py](scripts/image_grabber.py)
    - [camera_calibration.py](scripts/camera_calibration.py)

  - Run it:
    ```bash
    cd /home/GS_ICP_SLAM
    python -W ignore gs_icp_slam.py --dataset_path /path/to/your/dataset --config /path/to/your/config/caminfo.txt --rerun_viewer
    ```


## Troubleshooting
[rerun docker issue](https://github.com/rerun-io/rerun/issues/6835)

[Nvidia Developer Forum](https://forums.developer.nvidia.com/t/new-computer-install-gpu-docker-error/266084/6)

Feel free to reach out! :)
