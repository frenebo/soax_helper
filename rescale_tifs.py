from snakeutils.files import readable_dir
import os
import argparse
import matplotlib.pyplot as plt
import imageio
import cv2
from PIL import Image
from scipy.ndimage import zoom
import tifffile
import numpy as np

def rescale_multi_dim_arr(arr,rescale_factor):
    if len(arr.shape) > 3:
        raise Exception("Can't resize array with more than three dimensions")
    if len(arr.shape) == 3:
        depth = arr.shape[2]
    else:
        depth = None


    dims = arr.shape[:2]
    new_dims = []

    for dim in dims:
        new_dim = int(dim * rescale_factor)
        if new_dim == 0:
            raise Exception("Dimension {} in {} rescaled by factor {} becomes zero".format(dim,fp,args.rescale_factor))
        new_dims.append(new_dim)

    old_height = dims[0]
    old_width = dims[1]
    new_height = new_dims[0]
    new_width = new_dims[1]

    if depth is not None:
        print("  Resizing {}x{}, depth {} to {}x{}, depth {}".format(old_width,old_height,depth,new_width,new_height,depth))

        new_arr = np.zeros((new_height,new_width,depth),dtype=arr.dtype)
        for i in range(depth):
            new_arr[:,:,i] = cv2.resize(arr[i],dsize=(new_width,new_height))
    else:
        print("  Resizing {}x{} to {}x{}".format(old_width,old_height,new_width,new_height))
        new_arr = cv2.resize(arr,dsize=(new_width,new_height))

    return new_arr

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('rescale_factor',help="Scale factor, for example 0.5 to make tifs half scale")
    parser.add_argument('source_dir',type=readable_dir,help="Directory where source tif files are")
    parser.add_argument('target_dir',type=readable_dir)

    args = parser.parse_args()

    if float(args.rescale_factor) <= 0:
        raise Exception("Rescale factor must be positive")

    tif_files = [filename for filename in os.listdir(args.source_dir) if filename.endswith(".tif")]
    tif_files.sort()

    for filename in tif_files:
        fp = os.path.join(args.source_dir,filename)

        pil_img = Image.open(fp)

        # 3D tif images have attribute n_frames with non-zero value
        img_is_3d = getattr(pil_img, "n_frames", 1) != 1

        if img_is_3d:
            print("Processing {}".format(fp))
            arr = np.zeros((pil_img.height,pil_img.width,pil_img.n_frames),dtype=np.array(pil_img).dtype)
            for frame_idx in range(pil_img.n_frames):
                pil_img.seek(frame_idx)
                arr[:,:,frame_idx] = np.array(pil_img)
        else:
            arr = np.array(pil_img)

        resized_img = rescale_multi_dim_arr(arr,float(args.rescale_factor))

        new_fp = os.path.join(args.target_dir, "resized_{}_".format(args.rescale_factor) + filename)

        tifffile.imsave(new_fp, resized_img)

