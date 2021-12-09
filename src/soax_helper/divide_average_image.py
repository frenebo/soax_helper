import os
import numpy as np
from PIL import Image
from multiprocessing.pool import ThreadPool

from .snakeutils.logger import PrintLogger
from .snakeutils.files import has_one_of_extensions
from .snakeutils.tifimage import save_3d_tif, pil_img_3d_to_np_arr

def divide_average_image(source_dir, target_dir, logger=PrintLogger):
    source_tiffs = [filename for filename in os.listdir(source_dir) if has_one_of_extensions(filename, [".tif", ".tiff"])]
    source_tiffs.sort()

    if len(source_tiffs) == 0:
        logger.FAIL("No .tif/.tiff files found in {}".format(source_dir))
        return

    if len(source_tiffs) < 20:
        logger.log("Warning: less than 20 source tiffs. Dividing image average works best for large data sets.")

    first_pil_img = Image.open(os.path.join(source_dir, source_tiffs[0]))
    first_tiff_arr = pil_img_3d_to_np_arr(first_pil_img)
    img_shape = first_tiff_arr.shape

    sum_image = np.zeros(img_shape, dtype=np.double)

    logger.log("Finding average image\n")
    # image_count = 0
    for tiff_name in source_tiffs:
        tiff_path = os.path.join(source_dir, tiff_name)
        logger.success("   Reading {} ".format(tiff_path))
        pil_img = Image.open(tiff_path)
        np_arr = pil_img_3d_to_np_arr(pil_img)
        sum_image += np_arr

    average_image = (sum_image / len(source_tiffs))

    logger.log("Average image max: {} min: {}".format(average_image.max(), average_image.min()))
    if average_image.min() == 0:
        logger.FAIL("Cannot divide by average image, at some points the average image in {} has a brightness of zero".format(source_dir))

    image_mult_factor = np.reciprocal(average_image)
    image_mult_factor /= image_mult_factor.max()
    logger.log("Biggest division factor (inverse): {}".format(image_mult_factor.min()))

    for tiff_name in source_tiffs:
        image_path = os.path.join(source_dir, tiff_name)
        logger.log("Dividing {} by average".format(image_path))
        pil_img = Image.open(image_path)
        np_arr = pil_img_3d_to_np_arr(pil_img)

        divided_arr = np.multiply(np_arr.astype(np.double), image_mult_factor)
        divided_arr = divided_arr.astype(np_arr.dtype)

        save_tiff_path = os.path.join(target_dir, tiff_name)
        logger.success("    Saving divided image {}".format(save_tiff_path))
        save_3d_tif(save_tiff_path, np_arr)