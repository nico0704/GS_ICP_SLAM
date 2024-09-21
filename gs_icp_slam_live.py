# This code runs the gs_icp_slam algorithm with a stream of live data from a depth camera.
# Following args can be specified for the live stream version:
    # save_images: A flag that determines whether or not to save the captured images.
    # save_dir: Specifies the directory where the images will be saved.
    # stop_after: Sets the maximum number of images to capture and process (default is 2000).
    # fps: Defines the frame rate (frames per second) for capturing images (default is 30 fps).

import os
import torch
import torch.multiprocessing as mp
import sys
from datetime import datetime
import numpy as np
import time
import rerun as rr
sys.path.append(os.path.dirname(__file__))
from argparse import ArgumentParser
from arguments import SLAMParameters
from utils.traj_utils import TrajManager
from utils.graphics_utils import focal2fov
from scene.shared_objs import SharedCam, SharedGaussians, SharedPoints, SharedTargetPoints
from gaussian_renderer import render, network_gui
from mp_Tracker_live import Tracker
from mp_Mapper_live import Mapper
from camera import Camera

torch.multiprocessing.set_sharing_strategy('file_system')

class Pipe():
    def __init__(self, convert_SHs_python, compute_cov3D_python, debug):
        self.convert_SHs_python = convert_SHs_python
        self.compute_cov3D_python = compute_cov3D_python
        self.debug = debug
        
class GS_ICP_SLAM(SLAMParameters):
    def __init__(self, args):
        super().__init__()
        self.dataset_path = args.dataset_path
        self.output_path = args.output_path
        os.makedirs(self.output_path, exist_ok=True)
        self.verbose = args.verbose
        self.keyframe_th = float(args.keyframe_th)
        self.knn_max_distance = float(args.knn_maxd)
        self.overlapped_th = float(args.overlapped_th)
        self.max_correspondence_distance = float(args.max_correspondence_distance)
        self.trackable_opacity_th = float(args.trackable_opacity_th)
        self.overlapped_th2 = float(args.overlapped_th2)
        self.downsample_rate = int(args.downsample_rate)
        self.test = args.test
        self.save_results = args.save_results
        self.rerun_viewer = args.rerun_viewer
        
        # live cam params
        self.save_images = args.save_images
        self.save_dir = args.save_dir
        self.stop_after = args.stop_after
        self.fps = float(args.fps)
        
        if self.rerun_viewer:
            rr.init("3dgsviewer")
            rr.spawn(connect=False)
        
        # test camera
        print("Initializing test camera.")
        self.camera = Camera()
        self.camera_parameters = self.camera.get_calib_parameters()
        self.W = int(self.camera_parameters[0])
        self.H = int(self.camera_parameters[1])
        self.fx = float(self.camera_parameters[2])
        self.fy = float(self.camera_parameters[3])
        self.cx = float(self.camera_parameters[4])
        self.cy = float(self.camera_parameters[5])
        self.depth_scale = float(self.camera_parameters[6])
        self.depth_trunc = float(self.camera_parameters[7])
        self.downsample_idxs, self.x_pre, self.y_pre = self.set_downsample_filter(self.downsample_rate)
        
        try:
            mp.set_start_method('spawn', force=True)
        except RuntimeError:
            pass
        
        self.trajmanager = TrajManager(self.camera_parameters[8], self.dataset_path)
        
        # prepare directories to store images
        if self.save_images:
            self.rgb_path = os.path.join(self.dataset_path, "rgb")
            self.depth_path = os.path.join(self.dataset_path, "depth")
            os.makedirs(self.dataset_path, exist_ok=True)
            os.makedirs(self.rgb_path, exist_ok=True)
            os.makedirs(self.depth_path, exist_ok=True)
        
        print("Taking test images.")
        test_rgb_img, test_depth_img = self.camera.get_images()
        test_points, _, _, _ = self.downsample_and_make_pointcloud(test_depth_img, test_rgb_img)
        
        print("Stoping test camera.")
        self.camera.stop()
        self.camera = None

        # Get size of final poses
        num_final_poses = len(self.trajmanager.poses)
        
        # Shared objects
        self.shared_cam = SharedCam(FoVx=focal2fov(self.fx, self.W), FoVy=focal2fov(self.fy, self.H),
                                    image=test_rgb_img, depth_image=test_depth_img,
                                    cx=self.cx, cy=self.cy, fx=self.fx, fy=self.fy)
        self.shared_new_points = SharedPoints(test_points.shape[0])
        self.shared_new_gaussians = SharedGaussians(test_points.shape[0])
        self.shared_target_gaussians = SharedTargetPoints(10000000)
        self.end_of_dataset = torch.zeros((1)).int()
        self.is_tracking_keyframe_shared = torch.zeros((1)).int()
        self.is_mapping_keyframe_shared = torch.zeros((1)).int()
        self.target_gaussians_ready = torch.zeros((1)).int()
        self.new_points_ready = torch.zeros((1)).int()
        self.final_pose = torch.zeros((num_final_poses,4,4)).float()
        self.demo = torch.zeros((1)).int()
        self.is_mapping_process_started = torch.zeros((1)).int()
        self.iter_shared = torch.zeros((1)).int()
        
        self.shared_cam.share_memory()
        self.shared_new_points.share_memory()
        self.shared_new_gaussians.share_memory()
        self.shared_target_gaussians.share_memory()
        self.end_of_dataset.share_memory_()
        self.is_tracking_keyframe_shared.share_memory_()
        self.is_mapping_keyframe_shared.share_memory_()
        self.target_gaussians_ready.share_memory_()
        self.new_points_ready.share_memory_()
        self.final_pose.share_memory_()
        self.demo.share_memory_()
        self.is_mapping_process_started.share_memory_()
        self.iter_shared.share_memory_()
        
        self.demo[0] = args.demo
        self.mapper = Mapper(self)
        self.tracker = Tracker(self)

    def tracking(self, rank):
        self.tracker.run()
    
    def mapping(self, rank):
        self.mapper.run()

    def run(self):
        processes = []
        for rank in range(2):
            if rank == 0:
                p = mp.Process(target=self.tracking, args=(rank, ))
            elif rank == 1:
                p = mp.Process(target=self.mapping, args=(rank, ))
            p.start()
            processes.append(p)
        for p in processes:
            p.join()
        
    def run_viewer(self, lower_speed=True):
        if network_gui.conn == None:
            network_gui.try_connect()
        while network_gui.conn != None:
            if time.time()-self.last_t < 1/self.viewer_fps and lower_speed:
                break
            try:
                net_image_bytes = None
                custom_cam, do_training, self.pipe.convert_SHs_python, self.pipe.compute_cov3D_python, keep_alive, scaling_modifer = network_gui.receive()
                if custom_cam != None:
                    net_image = render(custom_cam, self.gaussians, self.pipe, self.background, scaling_modifer)["render"]
                    net_image_bytes = memoryview((torch.clamp(net_image, min=0, max=1.0) * 255).byte().permute(1, 2, 0).contiguous().cpu().numpy())
                    
                    # net_image = render(custom_cam, self.gaussians, self.pipe, self.background, scaling_modifer)["render_depth"]
                    # net_image = torch.concat([net_image,net_image,net_image], dim=0)
                    # net_image_bytes = memoryview((torch.clamp(net_image, min=0, max=7.0) * 50).byte().permute(1, 2, 0).contiguous().cpu().numpy())
                    
                self.last_t = time.time()
                network_gui.send(net_image_bytes, self.dataset_path) 
                if do_training and (not keep_alive):
                    break
            except Exception as e:
                network_gui.conn = None

    def set_downsample_filter( self, downsample_scale):
        # Get sampling idxs
        sample_interval = downsample_scale
        h_val = sample_interval * torch.arange(0,int(self.H/sample_interval)+1)
        h_val = h_val-1
        h_val[0] = 0
        h_val = h_val*self.W
        a, b = torch.meshgrid(h_val, torch.arange(0,self.W,sample_interval))
        # For tensor indexing, we need tuple
        pick_idxs = ((a+b).flatten(),)
        # Get u, v values
        v, u = torch.meshgrid(torch.arange(0,self.H), torch.arange(0,self.W))
        u = u.flatten()[pick_idxs]
        v = v.flatten()[pick_idxs]
        
        # Calculate xy values, not multiplied with z_values
        x_pre = (u-self.cx)/self.fx # * z_values
        y_pre = (v-self.cy)/self.fy # * z_values
        
        return pick_idxs, x_pre, y_pre

    def downsample_and_make_pointcloud(self, depth_img, rgb_img):
        
        colors = torch.from_numpy(rgb_img).reshape(-1,3).float()[self.downsample_idxs]/255
        z_values = torch.from_numpy(depth_img.astype(np.float32)).flatten()[self.downsample_idxs]/self.depth_scale
        filter = torch.where((z_values!=0)&(z_values<=self.depth_trunc))
        # print(z_values[filter].min())
        # Trackable gaussians (will be used in tracking)
        z_values = z_values
        x = self.x_pre * z_values
        y = self.y_pre * z_values
        points = torch.stack([x,y,z_values], dim=-1)
        colors = colors
        
        # untrackable gaussians (won't be used in tracking, but will be used in 3DGS)
        
        return points.numpy(), colors.numpy(), z_values.numpy(), filter[0].numpy()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--dataset_path", help="dataset path to store the images", default=None)
    parser.add_argument("--config", help="caminfo", default="configs/Replica/caminfo.txt")
    parser.add_argument("--output_path", help="output path", default="output/new_calib_test")
    parser.add_argument("--keyframe_th", default=0.7)
    parser.add_argument("--knn_maxd", default=99999.0)
    parser.add_argument("--verbose", action='store_true', default=False)
    parser.add_argument("--demo", action='store_true', default=False)
    parser.add_argument("--overlapped_th", default=5e-4)
    parser.add_argument("--max_correspondence_distance", default=0.02)
    parser.add_argument("--trackable_opacity_th", default=0.05)
    parser.add_argument("--overlapped_th2", default=5e-5)
    parser.add_argument("--downsample_rate", default=10)
    parser.add_argument("--test", default=None)
    parser.add_argument("--save_results", action='store_true', default=None)
    parser.add_argument("--rerun_viewer", action="store_true", default=False)
    parser.add_argument("--save_images", action='store_true', default=None)
    parser.add_argument("--save_dir", help="directory to save the taken images", default="dataset/custom_{}".format(datetime.now().strftime("%d%m%Y_%H_%M")))
    parser.add_argument("--stop_after", default=2000)
    parser.add_argument("--fps", default=30)
    
    args = parser.parse_args()

    gs_icp_slam = GS_ICP_SLAM(args)
    # gs_icp_slam.SLAM(1)
    gs_icp_slam.run()
