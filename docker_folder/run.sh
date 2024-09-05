XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -
chmod 777 $XAUTH
docker run  -d --gpus all -it --privileged --network=host --shm-size=12G -e NVIDIA_DRIVER_CAPABILITIES=all -e DISPLAY=$DISPLAY -v $XSOCK:$XSOCK -v $XAUTH:$XAUTH -e XAUTHORITY=$XAUTH -v /path/to/GS_ICP_SLAM:/home/GS_ICP_SLAM --name gsicp_exp1 gs_icp_slam_image