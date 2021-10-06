from collections import OrderedDict
import os
import argparse
import json
import time

from create_soax_param_files import error_string_or_parse_arg_or_range, create_soax_param_files
from xy_rescale_tiffs import xy_rescale_tiffs
from z_rescale_tiffs import z_rescale_tiffs
from auto_contrast_tiffs import auto_contrast_tiffs
from section_tiffs import section_tiffs
from run_soax import run_soax
from snakeutils.logger import RecordLogger, PrintLogger
from convert_snakes_to_json import convert_snakes_to_json
from join_sectioned_snakes import join_sectioned_snakes
from scale_json_snakes_to_units import scale_json_snakes_to_units
from make_orientation_fields import make_orientation_fields
from cindy_matrices_from_snakes import cindy_matrices_from_snakes
from do_bead_piv import do_bead_piv

from setup_app import (
    SoaxSetupApp,
    ZRescaleSetupForm,
    XYRescaleSetupForm,
    AutoContrastSetupForm,
    SectioningSetupForm,
    SoaxParamsSetupPage1Form,
    SoaxParamsSetupPage2Form,
    SoaxRunSetupForm,
    SnakesToJsonSetupForm,
    JoinSectionedSnakesSetupForm,
    ScaleJsonSnakesToUnitsSetupForm,
    MakeSnakeImagesSetupForm,
    MakeSnakeVideosSetupForm,
    MakeOrientationFieldsSetupForm,
    BeadPIVSetupForm,
    TubePIVSetupForm,
)

def perform_action(action_name, setting_strings, make_dirs, logger):
    if action_name == "rescale_tiffs":
        parsed_rescale_tiffs = RescaleSetupForm.parseSettings(setting_strings, make_dirs)
        rescale_tiffs(
            parsed_z_rescale_settings["batch_resample_path"],
            parsed_z_rescale_settings["source_tiff_dir"],
            parsed_z_rescale_settings["target_tiff_dir"],
            parsed_z_rescale_settings["xy_factor"],
            parsed_z_rescale_settings["z_factor"],
        )
    elif action_name == "auto_contrast_tiffs":
        parsed_auto_contrast_settings = AutoContrastSetupForm.parseSettings(setting_strings, make_dirs)
        auto_contrast_tiffs(
            parsed_auto_contrast_settings["source_tiff_dir"],
            parsed_auto_contrast_settings["target_tiff_dir"],
            parsed_auto_contrast_settings["max_cutoff_percent"],
            parsed_auto_contrast_settings["min_cutoff_percent"],
            parsed_auto_contrast_settings["workers_num"],
            logger=logger,
        )
    elif action_name == "section_tiffs":
        parsed_sectioning_settings = SectioningSetupForm.parseSettings(setting_strings, make_dirs)
        section_tiffs(
            parsed_sectioning_settings["section_max_size"],
            parsed_sectioning_settings["source_tiff_dir"],
            parsed_sectioning_settings["target_sectioned_tiff_dir"],
            logger=logger,
        )
    elif action_name == "create_soax_param_files":
        parsed_page1_params_settings = SoaxParamsSetupPage1Form.parseSettings(setting_strings, make_dirs)
        parsed_page2_params_settings = SoaxParamsSetupPage2Form.parseSettings(setting_strings, make_dirs)
        parsed_params_settings = {
            **parsed_page1_params_settings,
            **parsed_page2_params_settings,
        }
        create_soax_param_files(
            parsed_params_settings["params_save_dir"],
            alpha_start_stop_step=parsed_params_settings["alpha"],
            beta_start_stop_step=parsed_params_settings["beta"],
            gamma_start_stop_step=parsed_params_settings["gamma"],
            min_foreground_start_stop_step=parsed_params_settings["min_foreground"],
            ridge_threshold_start_stop_step=parsed_params_settings["ridge_threshold"],
            min_snake_length_start_stop_step=parsed_params_settings["min_snake_length"],
            gaussian_std_start_stop_step=parsed_params_settings["gaussian_std"],
            snake_point_spacing_start_stop_step=parsed_params_settings["snake_point_spacing"],
            external_factor_start_stop_step=parsed_params_settings["external_factor"],
            intensity_scaling_start_stop_step=parsed_params_settings["intensity_scaling"],
            stretch_factor_start_stop_step=parsed_params_settings["stretch_factor"],
            logger=logger,
        )
    elif action_name == "run_soax":
        parsed_soax_run_settings = SoaxRunSetupForm.parseSettings(setting_strings, make_dirs)

        run_soax(
            parsed_soax_run_settings["batch_soax_path"],
            parsed_soax_run_settings["source_tiff_dir"],
            parsed_soax_run_settings["param_files_dir"],
            parsed_soax_run_settings["target_snakes_dir"],
            parsed_soax_run_settings["soax_log_dir"],
            parsed_soax_run_settings["use_subdirs"],
            parsed_soax_run_settings["workers"],
            logger=logger,
        )
    elif action_name == "convert_snakes_to_json":
        parsed_snakes_to_json_settings = SnakesToJsonSetupForm.parseSettings(setting_strings, make_dirs)

        convert_snakes_to_json(
            parsed_snakes_to_json_settings["source_snakes_dir"],
            parsed_snakes_to_json_settings["target_json_dir"],
            parsed_snakes_to_json_settings["source_snakes_depth"],
            logger=logger,
        )
    elif action_name == "join_sectioned_snakes":
        parsed_join_sectioned_snakes_settings = JoinSectionedSnakesSetupForm.parseSettings(setting_strings, make_dirs)

        join_sectioned_snakes(
            parsed_join_sectioned_snakes_settings["source_json_dir"],
            parsed_join_sectioned_snakes_settings["target_json_dir"],
            source_jsons_depth=parsed_join_sectioned_snakes_settings["source_jsons_depth"],
            logger=logger,
        )
    elif action_name == "scale_json_snakes_to_units":
        parsed_scale_json_snakes_to_units = ScaleJsonSnakesToUnitsSetupForm.parseSettings(setting_strings, make_dir_if_not_present=make_dirs)

        scale_json_snakes_to_units(
            parsed_scale_json_snakes_to_units["source_json_dir"],
            parsed_scale_json_snakes_to_units["source_jsons_depth"],
            parsed_scale_json_snakes_to_units["target_json_dir"],
            parsed_scale_json_snakes_to_units["x_y_pixel_size_um"],
            parsed_scale_json_snakes_to_units["x_y_image_scale_factor"],
            parsed_scale_json_snakes_to_units["z_stack_spacing_um"],
            parsed_scale_json_snakes_to_units["unit_abbreviation"],
            logger=logger,
        )
    elif action_name == "make_orientation_fields":
        parsed_make_orientation_fields_settings = MakeOrientationFieldsSetupForm.parseSettings(setting_strings, make_dirs)

        make_orientation_fields(
            parsed_make_orientation_fields_settings["source_json_dir"],
            parsed_make_orientation_fields_settings["target_data_dir"],
            parsed_make_orientation_fields_settings["source_jsons_depth"],
            parsed_make_orientation_fields_settings["image_width"],
            parsed_make_orientation_fields_settings["image_height"],
            logger=logger,
        )
    elif action_name == "make_cindy_matrices_from_snakes":
        parsed_make_cindy_matrices_from_snakes_settings = MakeCindyMatricesFromSnakesSetupForm.parseSettings(setting_strings, make_dirs)

        make_cindy_matrices_from_snakes(
            parsed_make_cindy_matrices_from_snakes_settings["source_json_dir"],
            parsed_make_cindy_matrices_from_snakes_settings["source_jsons_depth"],
            parsed_make_cindy_matrices_from_snakes_settings["orientation_matrix_dir"],
            parsed_make_cindy_matrices_from_snakes_settings["position_matrix_dir"],
            logger=logger,
        )
    elif action_name == "do_bead_PIV":
        parsed_bead_PIV_settings = BeadPIVSetupForm.parseSettings(setting_strings, make_dirs)

        do_bead_piv(
            parsed_bead_PIV_settings["source_tiff_dir"],
            parsed_bead_PIV_settings["tiff_fn_letter_before_frame_num"],
            parsed_bead_PIV_settings["target_piv_data_dir"],
            parsed_bead_PIV_settings["x_y_pixel_size_um"],
            parsed_bead_PIV_settings["z_stack_spacing_um"],
            parsed_bead_PIV_settings["bead_diameter_um"],
            logger=logger,
        )
    elif action_name == "do_tube_PIV":
        parsed_tube_PIV_settings = TubePIVSetupForm.parseSettings(setting_strings, make_dirs)

        do_tube_piv(
            parsed_tube_PIV_settings["source_tiff_dir"],
            parsed_tube_PIV_settings["target_piv_data_dir"],
            logger=logger,
        )
    else:
        raise Exception("Unknown action name '{}'".format(action_name))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Soax Helper')
    parser.add_argument('--load-settings',default=None,help="Skip GUI, Run from settings loaded from JSON file")
    parser.add_argument('--save-settings',default=None,help="Save settings from GUI menu to JSON file")
    parser.add_argument('--do-not-run', default=False, action='store_true', help='Will load or save settings but will not run. Use if you want to just create settings but not run them')
    parser.add_argument('--make-dirs',default=False,action='store_true', help='If --load_settings, whether program should make directories in settings file is the directories don\'t exist already.')

    args = parser.parse_args()
    if args.load_settings is not None and args.save_settings is not None:
        raise Exception("Loading settings and saving settings is not supported"
            "(loading tells program to skip GUI, but saving is meant to store "
            "settings configured in GUI)")
    if args.load_settings is not None:
        if not args.load_settings.endswith(".json"):
            raise Exception("Invalid settings load file '{}': must be json file".format(args.load_settings))

        if not os.path.exists(args.load_settings):
            raise Exception("File '{}' does not exist".format(args.load_settings))

        with open(args.load_settings, "r") as f:
            action_configs = json.load(f)
    else:
        if args.save_settings is not None:
            if not args.save_settings.endswith(".json"):
                raise Exception("Cannot save settings as '{}', file must have '.json' extension".format(args.save_settings))
            if os.path.exists(args.save_settings):
                raise Exception("Cannot save settings as '{}', already exists".format(args.save_settings))
        app = SoaxSetupApp(make_dirs=args.make_dirs)
        app.run()

        action_configs = app.getActionConfigs()

        if args.save_settings is not None:
            with open(args.save_settings, "w") as f:
                json.dump(action_configs, f, indent=4)

    if args.do_not_run:
        exit()

    all_loggers = []
    all_times = []

    for action_conf in action_configs:
        action_name = action_conf["action"]
        action_settings = action_conf["settings"]

        start_time = time.time()

        action_logger = RecordLogger()
        all_loggers.append((action_name, action_logger))

        perform_action(action_name, action_settings, args.make_dirs, action_logger)

        end_time = time.time()
        elapsed = end_time - start_time
        all_times.append((action_name, elapsed))
        PrintLogger.log("{} took {} seconds".format(action_name, elapsed))

    for step_name, record_logger in all_loggers:
        if len(record_logger.errors) > 0:
            PrintLogger.error("ERRORS FROM {}".format(step_name))
            for err in record_logger.errors:
                PrintLogger.error("  " + err)

    for i, (step_name, seconds_taken) in enumerate(all_times):
        print("Step #{}, '{}' took {} seconds".format(i + 1, step_name, seconds_taken))

