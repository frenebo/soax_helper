import math
from multiprocessing.pool import ThreadPool
import os
import numpy as np
from PIL import Image
import tifffile

from ..snakeutils.tifimage import save_3d_tif, open_tiff_as_np_arr

def section_tiff(arg_dict):
    tiff_filepath = arg_dict["tiff_filepath"]
    sectioned_dir = arg_dict["sectioned_dir"]
    section_max_size = arg_dict["section_max_size"]
    logger = arg_dict["logger"]

    logger.log("Processing {}".format(tiff_filepath))

    img_arr = open_tiff_as_np_arr(tiff_filepath)
    height,width,depth = img_arr.shape

    # Ceil because we want to have slices on the smaller size if width/height/depth is not
    # exactly divisible by section_size
    height_slices = math.ceil(height / section_max_size)
    width_slices = math.ceil(width / section_max_size)
    depth_slices = math.ceil(depth / section_max_size)

    section_height = math.floor(height / height_slices)
    section_width = math.floor(width / width_slices)
    section_depth = math.floor(depth / depth_slices)

    height_boundaries = [i*section_height for i in range(height_slices)] + [height]
    width_boundaries = [i*section_width for i in range(width_slices)] + [width]
    depth_boundaries = [i*section_depth for i in range(depth_slices)] + [depth]

    for width_idx in range(width_slices):
        for height_idx in range(height_slices):
            for depth_idx in range(depth_slices):
                height_lower = height_boundaries[height_idx]
                height_upper = height_boundaries[height_idx + 1]
                width_lower = width_boundaries[width_idx]
                width_upper = width_boundaries[width_idx + 1]
                depth_lower = depth_boundaries[depth_idx]
                depth_upper = depth_boundaries[depth_idx + 1]

                # section filenames should be padded with zeros so they're same length.
                # ex. sec_0010-0020_0000-015_0990-1005.tif
                height_str_len = len(str(height))
                width_str_len = len(str(width))
                depth_str_len = len(str(depth))

                section_arr = img_arr[
                    height_lower:height_upper,
                    width_lower:width_upper,
                    depth_lower:depth_upper,
                ]

                section_filename = "sec_x{width_lower}-{width_upper}_y{height_lower}-{height_upper}_z{depth_lower}-{depth_upper}.tif".format(
                    width_lower=str(width_lower).zfill(width_str_len),
                    width_upper=str(width_upper).zfill(width_str_len),
                    height_lower=str(height_lower).zfill(height_str_len),
                    height_upper=str(height_upper).zfill(height_str_len),
                    depth_lower=str(depth_lower).zfill(depth_str_len),
                    depth_upper=str(depth_upper).zfill(depth_str_len),
                )
                section_filepath = os.path.join(sectioned_dir,section_filename)

                save_3d_tif(section_filepath,section_arr)

    section_num = width_slices*height_slices*depth_slices

    logger.success("  Split {} into {} sections in {}".format(
        tiff_filepath,
        section_num,
        sectioned_dir))

def section_tiffs(
    section_max_size,
    source_dir,
    target_dir,
    workers_num,
    logger,
    ):
    if section_max_size <= 0:
        logger.FAIL("Section max size must be positive. Invalid value {}".format(section_size))

    source_tiffs = [filename for filename in os.listdir(source_dir) if filename.endswith(".tif")]
    source_tiffs.sort()

    section_arg_dicts = []

    for tiff_fn in source_tiffs:
        tiff_fp = os.path.join(source_dir,tiff_fn)

        image_name_extensionless = os.path.splitext(tiff_fn)[0]

        sectioned_dir = os.path.join(target_dir, image_name_extensionless)

        if os.path.exists(sectioned_dir):
            logger.FAIL("Directory {} already exists".format(sectioned_dir))

        os.mkdir(sectioned_dir)

        section_arg_dicts.append({
            "tiff_filepath": tiff_fp,
            "sectioned_dir": sectioned_dir,
            "section_max_size": section_max_size,
            "logger": logger,
        })

    with ThreadPool(workers_num) as pool:
        future = pool.map(section_tiff, section_arg_dicts, chunksize=1)
