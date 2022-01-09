import os
import copy
from PIL import Image
import numpy as np
import decimal

from .snakeutils.files import find_tiffs_in_dir
from .create_regular_soax_param_files import create_regular_soax_param_files
from .snakeutils.tifimage import pil_img_3d_to_np_arr

def get_image_intensity_scaling(img_arr, logger):
    original_max_intensity = img_arr.max()

    if original_max_intensity == 0:
        logger.FAIL("TIFF has zero brightness everywhere, cannot intensity scale")

    # Is one divided by the
    # For example, an 8 bit tiff would have a max possible value of 255
    intensity_scaling_factor = 1.0 / float(original_max_intensity)

    return intensity_scaling_factor

def create_image_specific_soax_param_files(
    params_save_dir,
    original_tiff_dir,
    set_intensity_scaling_for_each_image,
    general_param_settings,
    logger,
):
    orig_tiffs = find_tiffs_in_dir(original_tiff_dir)

    for orig_tiff_fn in orig_tiffs:
        tiff_path = os.path.join(original_tiff_dir, orig_tiff_fn)
        image_name_without_extension = os.path.splitext(orig_tiff_fn)[0]
        image_params_dirpath = os.path.join(params_save_dir, image_name_without_extension)
        os.mkdir(image_params_dirpath)

        logger.log("Making parameter files for {} in {}".format(tiff_path, image_params_dirpath))

        image_param_settings = copy.deepcopy(general_param_settings)


        pil_img = Image.open(tiff_path)
        image_arr = pil_img_3d_to_np_arr(pil_img)

        if set_intensity_scaling_for_each_image:
            logger.log("Finding intensity scaling for {}".format(tiff_path))
            intensity_scaling = get_image_intensity_scaling(image_arr, logger)
            intensity_scaling = decimal.Decimal(intensity_scaling)
            logger.success("     Intensity scaling for {} is {}".format(tiff_path, intensity_scaling))
            image_param_settings["intensity_scaling"] = {
                "start": intensity_scaling,
                "stop": intensity_scaling,
                "step": decimal.Decimal(0),
            }

        create_regular_soax_param_files(
            image_params_dirpath,
            image_param_settings,
            logger=logger,
        )
