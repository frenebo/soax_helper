from multiprocessing.pool import ThreadPool
import os
import numpy as np
from PIL import Image

from .snakeutils.logger import PrintLogger
from .snakeutils.files import find_tiffs_in_dir
from .snakeutils.tifimage import save_3d_tif, pil_img_3d_to_np_arr

def intensity_scale_single_tiff(arg_dict):
    source_tiff_dir = arg_dict["source_tiff_dir"]
    tiff_fn = arg_dict["tiff_fn"]
    target_tiff_dir = arg_dict["target_tiff_dir"]
    logger = arg_dict["logger"]


    source_tiff_fp = os.path.join(source_tiff_dir,tiff_fn)
    logger.log("Performing intensity scaling on {}".format(source_tiff_fp))
    intensity_scaled_fp = os.path.join(target_tiff_dir, tiff_fn)
    pil_img = Image.open(source_tiff_fp)
    orig_image_arr = pil_img_3d_to_np_arr(pil_img)

    original_max_intensity = orig_image_arr.max()
    img_type_max_value = np.iinfo(orig_image_arr.dtype).max

    logger.log("    Image max intensity: {}/{}".format(original_max_intensity, img_type_max_value))

    if img_type_max_value == 0:
        logger.FAIL("TIFF {} has zero brightness every where, cannot intensity scale".format(source_tiff_fp))

    # Rescale intensity so new maximum is max possible value.
    # For example, an 8 bit tiff would have a max possible value of 255
    scale_factor = float(img_type_max_value) / original_max_intensity
    intensity_scaled_arr = orig_image_arr * scale_factor
    where_float_arr_exceeds_imgtype_max = intensity_scaled_arr >= img_type_max_value
    intensity_scaled_arr = intensity_scaled_arr.astype(orig_image_arr.dtype)
    # In case the float multiplication put any intensities slightly over max
    # (For example in 8 bit image, an error might put a brightness to 255.1)
    # Set them manually to the max (like 255 for example) to make sure the int value
    # doesn't wrap around to 0
    intensity_scaled_arr[where_float_arr_exceeds_imgtype_max] = img_type_max_value

    logger.log("    New max intensity: {}".format(intensity_scaled_arr.max()))

    save_3d_tif(intensity_scaled_fp,intensity_scaled_arr)

    logger.success("    Saved auto contrast pic as {}".format(intensity_scaled_fp))

def intensity_scale_tiffs(
    source_tiff_dir,
    target_tiff_dir,
    workers_num,
    logger=PrintLogger,
    ):

    source_tiffs = find_tiffs_in_dir(source_tiff_dir)
    source_tiffs.sort()

    if len(source_tiffs) == 0:
        logger.FAIL("No TIFF files found in {}".format(source_tiff_dir))
        return

    intensity_scale_arg_dicts = []
    for tiff_fn in source_tiffs:
        intensity_scale_arg_dicts.append({
            "source_tiff_dir": source_tiff_dir,
            "tiff_fn": tiff_fn,
            "target_tiff_dir": target_tiff_dir,
            "logger": logger,
        })

    with ThreadPool(workers_num) as pool:
        future = pool.map(intensity_scale_single_tiff, intensity_scale_arg_dicts, chunksize=1)
