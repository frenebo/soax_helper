import os

from create_soax_param_files import create_soax_param_files
from snakeutils.logger import PrintLogger
from snakeutils.files import has_one_of_extensions

def create_soax_param_files_by_image(
    target_dir,
    # start_stop_step_vals,
):
    raise NotImplementedError()

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
#     source_tifs = [filename for filename in os.listdir(source_images_dir) if has_one_of_extensions(filename, [".tif", ".tiff"])]
#     source_tifs.sort()
