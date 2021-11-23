import math
from multiprocessing.pool import ThreadPool
import os
import numpy as np
from PIL import Image

from snakeutils.logger import PrintLogger
from snakeutils.files import has_one_of_extensions
from snakeutils.tifimage import save_3d_tif, pil_img_3d_to_np_arr

def intensity_scale_single_tiff(arg_dict):
    source_dir = arg_dict["source_dir"]
    tiff_fn = arg_dict["tiff_fn"]
    target_dir = arg_dict["target_dir"]
    logger = arg_dict["logger"]


    source_tiff_fp = os.path.join(source_dir,tiff_fn)
    logger.log("Performing intensity scaling on {}".format(source_tiff_fp))
    intensity_scaled = os.path.join(target_dir, "intensity_scaled_" + tiff_fn)
    pil_img = Image.open(source_tiff_fp)
    image_arr = pil_img_3d_to_np_arr(pil_img)

    original_max_intensity = image_arr.max()
    tiff_datatype_max_value = np.iinfo(first_tiff_arr.dtype).max

    # Rescale intensity so new maximum is max possible value.
    # For example, an 8 bit tiff would have a max possible value of 255
    image_arr *= tiff_datatype_max_value / original_max_intensity

    save_3d_tif(image_arr,new_arr)

    logger.success("Saved auto contrast pic as {}".format(intensity_scaled))

def intensity_scale_tiffs(
    source_tiff_dir,
    target_tiff_dir,
    workers_num,
    logger=PrintLogger,
    ):

    source_tifs = [filename for filename in os.listdir(source_dir) if has_one_of_extensions(filename, [".tif", ".tiff"])]
    source_tifs.sort()

    if len(source_tifs) == 0:
        logger.FAIL("No .tif or .tiff files found in {}".format(source_dir))
        return

    # first_tiff_img = Image.open(os.path.join(source_dir, source_tifs[0]))
    intensity_scale_arg_dicts = []
    for tiff_fn in source_tifs:
        intensity_scale_arg_dicts.append({
            "source_dir": source_dir,
            "tiff_fn": tiff_fn,
            "target_dir": target_dir,
            "logger": logger,
        })

    with ThreadPool(workers_num) as pool:
        future = pool.map(intensity_scale_single_tiff, intensity_scale_arg_dicts, chunksize=1)
