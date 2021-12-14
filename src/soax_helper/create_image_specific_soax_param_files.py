import os
import copy
from PIL import Image
import numpy as np

from .snakeutils.logger import PrintLogger
from .snakeutils.files import has_one_of_extensions
from .create_regular_soax_param_files import create_regular_soax_param_files
from snakeutils.tifimage import pil_img_3d_to_np_arr

def get_image_intensity_scaling(img_arr, logger):
    original_max_intensity = image_arr.max()

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
    logger=PrintLogger
):
    orig_tiffs = [filename for filename in os.listdir(original_tiff_dir) if has_one_of_extensions(filename, [".tif", ".tiff"])]
    orig_tiffs.sort()

    for orig_tiff_fn in orig_tiffs:
        tiff_path = os.path.join(original_tiff_dir, tiff_path)
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


# def create_individual_image_soax_param_files(
#     target_dir,
#     source_images_dir,
#     init_z,
#     damp_z,
#     intensity_scaling, # {"type": "by_image"} or {"type": "start_stop_step", "value":{"start":..."stop":...,"step":...}}
#     # intensity_scaling_start_stop_step,
#     # gaussian_std_start_stop_step,
#     # ridge_threshold_start_stop_step,
#     # maximum_foreground_start_stop_step,
#     # minimum_foreground_start_stop_step,
#     # snake_point_spacing_start_stop_step,
#     # min_snake_length_start_stop_step,
#     # maximum_iterations_start_stop_step,
#     # change_threshold_start_stop_step,
#     # check_period_start_stop_step,
#     # alpha_start_stop_step,
#     # beta_start_stop_step,
#     # gamma_start_stop_step,
#     # external_factor_start_stop_step,
#     # stretch_factor_start_stop_step,
#     # number_of_background_radial_sectors_start_stop_step,
#     # background_z_xy_ratio_start_stop_step,
#     # radial_near_start_stop_step,
#     # radial_far_start_stop_step,
#     # delta_start_stop_step,
#     # overlap_threshold_start_stop_step,
#     # grouping_distance_threshold_start_stop_step,
#     # grouping_delta_start_stop_step,
#     # minimum_angle_for_soac_linking_start_stop_step,
#     logger=PrintLogger,
#     ):
#     source_tiffs = [filename for filename in os.listdir(source_images_dir) if has_one_of_extensions(filename, [".tif", ".tiff"])]
#     source_tiffs.sort()
