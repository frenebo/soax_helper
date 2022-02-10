from skimage.transform import resize
from multiprocessing.pool import ThreadPool
import numpy as np
import os
import imageio
import cv2
from PIL import Image
from scipy.ndimage import zoom

from .snakeutils.files import find_files_or_folders_at_depth
from .snakeutils.tifimage import save_3d_tif, open_tiff_as_np_arr

def resize_frame(frame_arr, new_dims):
    data_type_max =  np.iinfo(frame_arr.dtype).max
    float_frame_arr = frame_arr.astype('float64')
    # array of floats, with values from 0.0 to 1.0
    float_frame_arr = float_frame_arr / data_type_max
    # print("FLOAT ARR: min: {}, max: {}".format(np.min(float_frame_arr), np.max(float_frame_arr)))
    pil_img = Image.fromarray(float_frame_arr)
    resized_pil_img = pil_img.resize(new_dims, Image.LANCZOS)
    resized_float_arr = np.array(resized_pil_img)
    # Lanczos resize may give negative or greater than 1 pixel values, set these to 0 and 1 respectively
    resized_float_arr[resized_float_arr < 0] = 0
    resized_float_arr[resized_float_arr > 1] = 1

    # print("RESIZED FLOAT min: {}, max: {}".format(np.min(resized_float_arr), np.max(resized_float_arr)))
    resized_orig_type_arr = (resized_float_arr * data_type_max).astype(frame_arr.dtype)
    # print("RESIZED ORIG type min: {}, max: {}".format(np.min(resized_orig_type_arr), np.max(resized_orig_type_arr)))
    # print("Resized frame")
    return resized_orig_type_arr

def xy_rescale_3D_arr(arr, new_width, new_height):
    old_height, old_width, depth = arr.shape

    new_arr = np.zeros((new_height,new_width,depth),dtype=arr.dtype)
    for i in range(depth):
        new_arr[:,:,i] = resize_frame(arr[:,:,i],(new_width,new_height))

    return new_arr

def rescale_single_tiff(arg_dict):
    source_tiff_path = arg_dict["source_tiff_path"]
    target_tiff_path = arg_dict["target_tiff_path"]
    input_dims = arg_dict["input_dims"]
    output_dims = arg_dict["output_dims"]
    logger = arg_dict["logger"]

    old_width = input_dims[0]
    old_height = input_dims[1]
    old_depth = input_dims[2]

    new_width = output_dims[0]
    new_height = output_dims[1]
    new_depth = output_dims[2]

    logger.log("Loading tiff {} to rescale".format(source_tiff_path))

    img_arr = open_tiff_as_np_arr(source_tiff_path)
    # width,height,depth
    observed_dims = (img_arr.shape[1],img_arr.shape[0],img_arr.shape[2])

    # check dimensions match
    if observed_dims != tuple(input_dims):
        logger.FAIL("Problem resizing {}, expected original dimensions {} but dimensions are actually {}".format(
            source_tiff_path,
            input_dims,
            observed_dims,
        ))


    if new_depth != old_depth:
        # print("Shape before rescaling shape: {}".format(img_arr.shape))
        # move depth axis to height dimension (height,width,depth) -> (depth,width,height)
        img_arr = np.moveaxis(img_arr, 2, 0)
        # print("Moved axis, now {}".format(img_arr.shape))

        # resize in depth direction
        img_arr = xy_rescale_3D_arr(img_arr, img_arr.shape[1], new_depth)
        # print("Resized, now {}".format(img_arr.shape))

        # move depth axis back (depth,width,height) -> (height,width,depth)
        img_arr = np.moveaxis(img_arr, 0, 2)
        # print("Shape after rescaling depth: {}".format(img_arr.shape))


    # resize in xy direction
    if new_height != old_height or new_width != old_width:
        # print("Shape before resizing xy: {}".format(img_arr.shape))
        img_arr = xy_rescale_3D_arr(img_arr, new_width, new_height)
        # print("Shape after resizing xy: {}".format(img_arr.shape))

    save_3d_tif(target_tiff_path,img_arr)
    logger.log("  Saved rescaled tiff as {}".format(target_tiff_path))

def rescale_tiffs(
    source_tiff_dir,
    target_tiff_dir,
    input_dims,
    output_dims,
    workers_num,
    logger,
    ):

    source_tiffs_info = find_files_or_folders_at_depth(source_tiff_dir, 0, file_extensions=[".tif", ".tiff"])

    rescale_tiffs_arg_dicts = []

    for source_tiff_containing_dirpath, tiff_fn in source_tiffs_info:
        source_tiff_fp = os.path.join(source_tiff_containing_dirpath, tiff_fn)
        dir_relpath = os.path.relpath(source_tiff_containing_dirpath, source_tiff_dir)
        target_tiff_dirpath = os.path.join(target_tiff_dir, dir_relpath)
        target_tiff_fp = os.path.join(target_tiff_dirpath, tiff_fn)

        if not os.path.isdir(target_tiff_dirpath):
            if os.path.exists(target_tiff_dirpath):
                logger.FAIL("Cannot save resized images to {}, path exists but is not dir".format(target_tiff_dirpath))
            else:
                os.makedirs(target_tiff_dirpath)

        rescale_tiffs_arg_dicts.append({
            "source_tiff_path": source_tiff_fp,
            "target_tiff_path": target_tiff_fp,
            "input_dims": input_dims,
            "output_dims": output_dims,
            "logger": logger,
        })

    with ThreadPool(workers_num) as pool:
        future = pool.map(rescale_single_tiff, rescale_tiffs_arg_dicts, chunksize=1)
