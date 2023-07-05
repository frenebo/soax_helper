import os
import copy
from PIL import Image
import numpy as np
import decimal

from ..snakeutils.files import find_tiffs_in_dir
from ..snakeutils.tifimage import open_tiff_as_np_arr
from .create_regular_soax_param_files import create_regular_soax_param_files

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


        image_arr = open_tiff_as_np_arr(tiff_path)

        if set_intensity_scaling_for_each_image:
            logger.log("Finding intensity scaling for {}".format(tiff_path))
            float_intensity_scaling = get_image_intensity_scaling(image_arr, logger)
            # Convert to string with 12 significant digits - so decimal doesn't have way too many
            # unnecessary digits
            str_intensity_scaling = "{0:.12g}".format(float_intensity_scaling)
            intensity_scaling = decimal.Decimal(str_intensity_scaling)
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
