from snakeutils.files import readable_dir, has_one_of_extensions
from snakeutils.tifimage import save_3d_tif, tiff_img_3d_to_arr
from skimage.transform import resize
import os
import argparse
import matplotlib.pyplot as plt
import imageio
import cv2
from PIL import Image
from scipy.ndimage import zoom
import tifffile
import numpy as np
from snakeutils.logger import PrintLogger

def resize_frame(frame_arr, new_dims):
    data_type_max =  np.iinfo(frame_arr.dtype).max
    float_frame_arr = frame_arr.astype('float64')
    float_frame_arr = float_frame_arr / data_type_max
    pil_img = Image.fromarray(float_frame_arr)
    resized_pil_img = pil_img.resize(new_dims, Image.ANTIALIAS)
    resized_float_arr = np.array(resized_pil_img)
    return (resized_float_arr * data_type_max).astype(frame_arr.dtype)

def rescale_multi_dim_arr(arr,rescale_factor,logger):
    if len(arr.shape) > 3:
        logger.FAIL("Can't resize array with more than three dimensions")

    if len(arr.shape) == 3:
        depth = arr.shape[2]
    else:
        depth = None


    dims = arr.shape[:2]
    new_dims = []

    for dim in dims:
        new_dim = int(dim * rescale_factor)
        if new_dim == 0:
            logger.FAIL("Dimension {} in {} rescaled by factor {} becomes zero".format(dim,fp,args.rescale_factor))
        new_dims.append(new_dim)

    old_height = dims[0]
    old_width = dims[1]
    new_height = new_dims[0]
    new_width = new_dims[1]

    if depth is not None:
        logger.log("  Resizing {}x{}, depth {} to {}x{}, depth {}".format(old_width,old_height,depth,new_width,new_height,depth))

        new_arr = np.zeros((new_height,new_width,depth),dtype=arr.dtype)
        for i in range(depth):
            # pil_frame = Image
            # new_arr[:,:,i] = cv2.resize(arr[:,:,i],dsize=(new_width,new_height))
            new_arr[:,:,i] = resize_fame(arr[:,:,i],(new_width,new_height))
    else:
        logger.log("  Resizing {}x{} to {}x{}".format(old_width,old_height,new_width,new_height))
        new_arr = resize_frame(arr,(new_width,new_height))
        # new_arr = cv2.resize(arr,dsize=(new_width,new_height), interpolation=cv2.INTER_CUBIC)

    return new_arr

def xy_rescale_tiffs(source_dir,target_dir,rescale_factor,logger=PrintLogger):
    tiff_files = [filename for filename in os.listdir(source_dir) if has_one_of_extensions(filename, [".tif", ".tiff"])]
    tiff_files.sort()

    for src_filename in tiff_files:
        fp = os.path.join(source_dir,src_filename)
        logger.log("Rescaling {}".format(fp))

        pil_img = Image.open(fp)

        # 3D tif images have attribute n_frames with non-zero value
        img_is_3d = getattr(pil_img, "n_frames", 1) != 1

        if img_is_3d:
            arr = tiff_img_3d_to_arr(pil_img)
        else:
            arr = np.array(pil_img)
        logger.log("Orig shape: {}".format(arr.shape))
        resized_img = rescale_multi_dim_arr(arr,rescale_factor,logger)
        logger.log("New shape: {}".format(resized_img.shape))
        new_fn = "{}resized_".format(rescale_factor) + src_filename
        new_fp = os.path.join(target_dir, new_fn)
        logger.log("  Saving rescaled image as {}".format(new_fp))

        if img_is_3d:
            save_3d_tif(new_fp,resized_img)
        else:
            tifffile.imsave(new_fp, resized_img)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('source_dir',type=readable_dir,help="Directory where source tif files are")
    parser.add_argument('target_dir',type=readable_dir)
    parser.add_argument('rescale_factor',type=float,help="Scale factor, for example 0.5 to make tiffs half scale")

    args = parser.parse_args()

    if args.rescale_factor <= 0:
        raise Exception("Rescale factor must be positive")

    xy_rescale_tiffs(args.source_dir, args.target_dir, args.rescale_factor)
