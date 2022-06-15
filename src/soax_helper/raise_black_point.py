import os
import numpy as np
from PIL import Image
from multiprocessing.pool import ThreadPool
from .snakeutils.files import find_tiffs_in_dir
from .snakeutils.tifimage import save_3d_tif, open_tiff_as_np_arr

def raise_black_point(source_tiff_dir, target_dir, black_pix_level, logger):
    source_tiffs = find_tiffs_in_dir(source_tiff_dir)

    if len(source_tiffs) == 0:
        logger.FAIL("No .tif/.tiff files found in {}".format(source_tiff_dir))
        return


    for tiff_name in source_tiffs:
        image_path = os.path.join(source_tiff_dir, tiff_name)
        logger.log("Subtracting {} from pixel brightnesses in {}".format(black_pix_level, image_path))

        np_arr = open_tiff_as_np_arr(image_path)

        new_arr = np_arr - black_pix_level
        new_arr[np_arr <= black_pix_level] = 0
        save_tiff_path = os.path.join(target_tiff_dir, tiff_name)
        logger.success("    Saving raised black point image {}".format(save_tiff_path))
        save_3d_tif(save_tiff_path, new_arr)

        # divided_arr = np.multiply(np_arr.astype(np.double), image_mult_factor)
        # divided_arr = divided_arr.astype(np_arr.dtype)

        # save_tiff_path = os.path.join(target_dir, tiff_name)
        # logger.success("    Saving divided image {}".format(save_tiff_path))
        # save_3d_tif(save_tiff_path, np_arr)
