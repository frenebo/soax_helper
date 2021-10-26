from snakeutils.files import has_one_of_extensions
from snakeutils.tifimage import save_3d_tif, pil_img_3d_to_np_arr
import os
from PIL import Image
import tifffile
import numpy as np
from snakeutils.logger import PrintLogger

def resize_frame(frame_arr, new_dims):
    data_type_max =  np.iinfo(frame_arr.dtype).max
    float_frame_arr = frame_arr.astype('float64')
    # array of floats, with values from 0.0 to 1.0
    float_frame_arr = float_frame_arr / data_type_max
    print("FLOAT ARR: min: {}, max: {}".format(np.min(float_frame_arr), np.max(float_frame_arr)))
    pil_img = Image.fromarray(float_frame_arr)
    resized_pil_img = pil_img.resize(new_dims, Image.LANCZOS)
    resized_float_arr = np.array(resized_pil_img)
    # Lanczos resize may give negative or greater than 1 pixel values, set these to 0 and 1 respectively
    resized_float_arr[resized_float_arr < 0] = 0
    resized_float_arr[resized_float_arr > 1] = 1

    print("RESIZED FLOAT min: {}, max: {}".format(np.min(resized_float_arr), np.max(resized_float_arr)))
    resized_orig_type_arr = (resized_float_arr * data_type_max).astype(frame_arr.dtype)
    print("RESIZED ORIG type min: {}, max: {}".format(np.min(resized_orig_type_arr), np.max(resized_orig_type_arr)))
    return resized_orig_type_arr

def xy_rescale_3D_arr(arr,rescale_factor,logger):
    depth = arr.shape[2]


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

    logger.log("  Resizing {}x{}, depth {} to {}x{}, depth {}".format(
        old_width,old_height,depth,new_width,new_height,depth))

    new_arr = np.zeros((new_height,new_width,depth),dtype=arr.dtype)
    for i in range(depth):
        new_arr[:,:,i] = resize_fame(arr[:,:,i],(new_width,new_height))


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

        if not img_is_3d:
            logger.FAIL("2D image rescaling not supported")

        logger.log("Orig shape: {}".format(arr.shape))
        resized_img = xy_rescale_3D_arr(arr,rescale_factor,logger)
        logger.log("New shape: {}".format(resized_img.shape))
        new_fn = "{}resized_".format(rescale_factor) + src_filename
        new_fp = os.path.join(target_dir, new_fn)
        logger.log("  Saving rescaled image as {}".format(new_fp))

        save_3d_tif(new_fp,resized_img)
