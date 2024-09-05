#!/bin/bash

set -e

MOUNTED_DIR="/home/GS_ICP_SLAM"
CLONED_DIR="/home/cloned_GS_ICP_SLAM"

echo "Cloning GS-ICP_SLAM repository..."
git clone --recursive https://github.com/Lab-of-AI-and-Robotics/GS_ICP_SLAM.git "$CLONED_DIR"

echo "Removing existing submodules directory in the mounted GS_ICP_SLAM directory..."
rm -rf "$MOUNTED_DIR/submodules"

echo "Copying submodules directory from the cloned repository to the mounted GS_ICP_SLAM directory..."
cp -r "$CLONED_DIR/submodules" "$MOUNTED_DIR/"

echo "Navigating to fast_gicp directory in the mounted GS_ICP_SLAM..."
cd "$MOUNTED_DIR/submodules/fast_gicp"

echo "Creating build directory..."
mkdir build
cd build

echo "Running cmake..."
cmake ..

echo "Running make..."
make -j4

cd ..

echo "Installing fast_gicp..."
python setup.py install --user

echo "Installing diff-gaussian-rasterization..."
pip install "$MOUNTED_DIR/submodules/diff-gaussian-rasterization"

echo "Installing simple-knn..."
pip install "$MOUNTED_DIR/submodules/simple-knn"

echo "Cleaning up cloned repository..."
rm -rf "$CLONED_DIR"

echo "Setup complete!"
