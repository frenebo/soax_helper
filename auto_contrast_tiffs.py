import math
from multiprocessing.pool import ThreadPool
import os
import numpy as np
from PIL import Image
import tifffile

from snakeutils.logger import PrintLogger
from snakeutils.files import has_one_of_extensions
from snakeutils.tifimage import save_3d_tif, pil_img_3d_to_np_arr

def auto_contrast_single_tiff(arg_dict):
    source_dir   = arg_dict["source_dir"]
    tiff_fn      = arg_dict["tiff_fn"]
    target_dir   = arg_dict["target_dir"]
    max_cutoff   = arg_dict["max_cutoff"]
    min_cutoff   = arg_dict["min_cutoff"]
    scale_factor = arg_dict["scale_factor"]
    new_max      = arg_dict["new_max"]
    logger       = arg_dict["logger"]
    images_are_3d = arg_dict["images_are_3d"]

    tiff_fp = os.path.join(source_dir,tiff_fn)
    logger.log("Performing auto contrast on {}".format(tiff_fp))
    auto_contrast_fp = os.path.join(target_dir, "auto_contrast_" + tiff_fn)

    pil_img = Image.open(tiff_fp)

    image_arr = pil_img_3d_to_np_arr(pil_img)

    over_max_places = image_arr >= max_cutoff
    under_min_places = image_arr <= min_cutoff

    # float_arr = image_arr.astype(np.float64)
    new_arr = (image_arr - min_cutoff)* scale_factor

    new_arr = new_arr.astype(image_arr.dtype)
    new_arr[over_max_places] = new_max
    new_arr[under_min_places] = 0

    # logger.log("New min:  {}".format(new_arr.min()))
    # logger.log("New max: {}".format(new_arr.max()))

    if images_are_3d:
        save_3d_tif(auto_contrast_fp,new_arr)
    else:
        tifffile.imsave(auto_contrast_fp,new_arr)
    logger.success("Saved auto contrast pic as {}".format(auto_contrast_fp))


def auto_contrast_tiffs(
    source_dir,
    target_dir,
    max_cutoff_percent,
    min_cutoff_percent,
    workers_num,
    logger=PrintLogger,
    ):
    source_tifs = [filename for filename in os.listdir(source_dir) if has_one_of_extensions(filename, [".tif", ".tiff"])]
    source_tifs.sort()

    if len(source_tifs) == 0:
        logger.error("No .tif files found in {}".format(source_dir))
        return

    first_tiff_img = Image.open(os.path.join(source_dir, source_tifs[0]))

    first_tiff_arr = pil_img_3d_to_np_arr(first_tiff_img)

    max_cutoff = np.percentile(first_tiff_arr,max_cutoff_percent)
    min_cutoff = np.percentile(first_tiff_arr,min_cutoff_percent)

    logger.log("Rescaling range to max val {}".format(max_cutoff))
    new_max = np.iinfo(first_tiff_arr.dtype).max
    scale_factor = float(new_max)/float(max_cutoff - min_cutoff)

    logger.log("Data type {} with max value {}".format(first_tiff_arr.dtype, new_max))

    contrast_arg_dicts = []

    for tiff_fn in source_tifs:
        contrast_arg_dicts.append({
            "source_dir": source_dir,
            "tiff_fn": tiff_fn,
            "target_dir": target_dir,
            "max_cutoff": max_cutoff,
            "min_cutoff": min_cutoff,
            "scale_factor": scale_factor,
            "new_max": new_max,
            "logger": logger,
            "images_are_3d": images_are_3d,
        })

    with ThreadPool(workers_num) as pool:
        future = pool.map(auto_contrast_single_tiff, contrast_arg_dicts)
