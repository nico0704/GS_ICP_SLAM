<div align=center>

# RGBD GS-ICP SLAM - Fork

**This is a modified fork of the original RGBD GS-ICP SLAM repository.**  
While keeping the foundation provided by Seongbo Ha, Jiung Yeon, and Hyeonwoo Yu, we have made some modifications to expand its functionality and support new use cases. This version includes support for custom datasets, Docker improvements, Unity visualization tools, and live data streaming capabilities. Below, you’ll find details about our contributions, followed by the original README from the authors.

Thanks to @[Johanna Rompf](https://github.com/jojo892), @[Tim Liehr](https://github.com/BrI4n99) @[Leon Kratz](https://github.com/leon-kratz), @[Alexander Jost](https://github.com/Abraxius), @[Nico Schroeder](https://github.com/nico0704)

</div>

---

## Our Contributions

### 1. Custom Data Compatibility
We extended the algorithm to support custom datasets, allowing it to work effectively with data sources that lack ground-truth poses. This involved updates across core files, that might be added to the original repo soon [PR #47](https://github.com/Lab-of-AI-and-Robotics/GS_ICP_SLAM/pull/47).


### 2. Unity Visualization Tools
A [setup guide](3D_Visualization/unity_setup_guide.md) and [converter](3D_Visualization/ply_converter.py) were added to enable Unity-based visualization of the GS-ICP-SLAM results. Additionally example visualizations of TUM, Replica and our custom data were uploaded ([visualizations](3D_Visualization/visus.md)).


### 3. Live Camera Streaming
To enable real-time testing, we incorporated live camera support, allowing data to be streamed and processed live by the algorithm. This makes it possible to observe performance in a live setting. See the following files:
  - [camera.py](camera.py): Class that controls an Intel RealSense camera (D400-series) to capture color and depth images.
  - [gs_icp_slam_live.py](gs_icp_slam_live.py): Running the algorithm with live captured data.
  - [mp_Tracker_live.py](mp_Tracker_live.py): Adjustments for working with the live data.


### 4. Docker Enhancements
We revamped Docker support to simplify environment setup and execution:
   - **Dockerfile Adjustments**: Improved the [Dockerfile](docker_folder/Dockerfile) to make build process work.
   - **Run Script**: Added [run.sh](docker_folder/run.sh) to facilitate running the algorithm and rerun viewer inside the container.
   - **Submodule Setup Script**: Included a shell script to handle submodule installation [install_submodules.sh](docker_folder/install_submodules.sh).
   - **Docker Documentation**: Created an in-depth [README.md](docker_folder/README.md) within the [docker_folder](docker_folder), detailing setup and execution steps for running the algorithm with custom data and Docker.

---

### Some visualizations of our custom data:

<img src="3D_Visualization/rerun/gang.gif" width="640" height="480" /><br><br>

Feel free to reach out!

Below is the original README from the authors of RGBD GS-ICP SLAM:


<div align=center>

# RGBD GS-ICP SLAM

Seongbo Ha, Jiung Yeon, Hyeonwoo Yu

<h3 align="center"> ECCV 2024 </h3>

[Paper](https://arxiv.org/abs/2403.12550) | [Video](https://www.youtube.com/watch?v=e-bHh_uMMxE&t)

![github (1)](https://github.com/Lab-of-AI-and-Robotics/GS_ICP_SLAM/assets/34827206/5722e8f4-165d-4093-8064-a7ed5d9ea008)

</div>

This repository is intended to substantiate the results reported in the paper. Additional features including visualization tools will be updated soon!

## Environments
Install requirements
```bash
conda create -n gsicpslam python==3.9
conda activate gsicpslam
conda install pytorch==2.0.0 torchvision==0.15.0 torchaudio==2.0.0 pytorch-cuda=11.8 -c pytorch -c nvidia
pip install -r requirements.txt
```
Also, PCL is needed for fast-gicp submodule.

Install submodules

```bash
conda activate gsicpslam
pip install submodules/diff-gaussian-rasterization
pip install submodules/simple-knn

cd submodules/fast_gicp
mkdir build
cd build
cmake ..
make
cd ..
python setup.py install --user
```


## Datasets

- Replica
  - Download
    ```bash
    bash download_replica.sh
    ```
  - Configure
  
    Please modify the directory structure to ours.

    The original structure
    ```bash
    Replica
        - room0
            - results (contain rgbd images)
                - frame000000.jpg
                - depth000000.jpg
                ...
            - traj.txt
        ...
    ```
    Our structure
    ```bash
    Replica
        - room0
            - images (contain rgb images)
                - frame000000.jpg
                ...
            - depth_images (contain depth images)
                - depth000000.jpg
                ...
            - traj.txt
        ...
    ```    

- TUM-RGBD
  - Download
    ```bash
        bash download_tum.sh
    ```

## Run
- Limited to 30 FPS
    ```bash
        # Replica
        bash replica.sh
        # TUM
        bash tum.sh
    ```

- Unlimited tracking speed
    ```bash
        # Replica
        bash replica_unlimit.sh
        # TUM
        bash tum_unlimit.sh
    ```

## Installing SIBR Viewer
```bash
cd SIBR_viewers
cmake -Bbuild . -DCMAKE_BUILD_TYPE=Release
cmake --build build -j24 --target install
```

## Real-time demo
### Using rerun.io viewer

Rerun viewer shows the means of trackable Gaussians, and rendered image from reconstructed 3dgs map.

![GIFMaker_me](https://github.com/Lab-of-AI-and-Robotics/GS_ICP_SLAM/assets/34827206/b4715071-2e4a-4d17-b7a2-612bbd32dbd0)

```bash
python -W ignore gs_icp_slam.py --rerun_viewer
```


### Using SIBR viewer
```bash
python -W ignore gs_icp_slam.py --dataset_path dataset/Replica/office0 --verbose

# In other terminal
cd SIBR_viewers
./install/bin/SIBR_remoteGaussian_app --rendering-size 1280 720
```

## Docker
Please see the README.md in the docker_files folder.
