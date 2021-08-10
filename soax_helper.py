from collections import OrderedDict
import os
import argparse
import json
import time

from create_param_files import error_string_or_parse_arg_or_range
from xy_rescale_tiffs import xy_rescale_tiffs
from z_rescale_tiffs import z_rescale_tiffs
from auto_contrast_tiffs import auto_contrast_tiffs
from section_tiffs import section_tiffs
from create_param_files import create_param_files
from run_soax import run_soax
from snakeutils.logger import RecordLogger, PrintLogger
from convert_snakes_to_json import convert_snakes_to_json
from join_sectioned_snakes import join_sectioned_snakes
from make_snake_images import make_snake_images
from make_videos import make_videos
from make_orientation_fields import make_orientation_fields

from setup_app import (
    SoaxSetupApp,
    ZRescaleSetupForm,
    XYRescaleSetupForm,
    AutoConstrastSetupForm,
    SectioningSetupForm,
    ParamsSetupForm,
    SoaxRunSetupForm,
    SnakesToJsonSetupForm,
    JoinSectionedSnakesSetupForm,
    MakeSnakeImagesSetupForm,
    MakeSnakeVideosSetupForm,
    MakeOrientationFieldsSetupForm,
)

def perform_action(action_name, setting_strings, make_dirs, logger):
    if action_name == "z_rescale_tiffs":
        parsed_z_rescale_settings = ZRescaleSetupForm.parseSettings(setting_strings, make_dirs_if_not_present=make_dirs)
        z_rescale_tiffs(
            parsed_z_rescale_settings["batch_resample_path"],
            parsed_z_rescale_settings["source_tiff_dir"],
            parsed_z_rescale_settings["target_tiff_dir"],
            parsed_z_rescale_settings["rescale_factor"],
            logger=logger
        )
    elif action_name == "xy_rescale_tiffs":
        parsed_xy_rescale_settings = XYRescaleSetupForm.parseSettings(setting_strings, make_dirs_if_not_present=make_dirs)
        xy_rescale_tiffs(
            parsed_xy_rescale_settings["source_tiff_dir"],
            parsed_xy_rescale_settings["target_tiff_dir"],
            parsed_xy_rescale_settings["rescale_factor"],
            logger=logger
        )
    elif action_name == "auto_contrast_tiffs":
        parsed_auto_contrast_settings = AutoConstrastSetupForm.parseSettings(setting_strings, make_dirs_if_not_present=make_dirs)
        auto_contrast_tiffs(
            parsed_auto_contrast_settings["source_tiff_dir"],
            parsed_auto_contrast_settings["target_tiff_dir"],
            parsed_auto_contrast_settings["max_cutoff_percent"],
            parsed_auto_contrast_settings["min_cutoff_percent"],
            logger=logger,
        )
    elif action_name == "section_tiffs":
        parsed_sectioning_settings = SectioningSetupForm.parseSettings(setting_strings, make_dirs_if_not_present=make_dirs)
        section_tiffs(
            parsed_sectioning_settings["section_max_size"],
            parsed_sectioning_settings["source_tiff_dir"],
            parsed_sectioning_settings["target_sectioned_tiff_dir"],
            logger=logger,
        )
    elif action_name == "create_param_files":
        parsed_params_settings = ParamsSetupForm.parseSettings(setting_strings, make_dirs_if_not_present=make_dirs)
        create_param_files(
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
            logger=logger,
        )
    elif action_name == "run_soax":
        parsed_soax_run_settings = SoaxRunSetupForm.parseSettings(setting_strings, make_dirs_if_not_present=make_dirs)

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
        parsed_snakes_to_json_settings = SnakesToJsonSetupForm.parseSettings(setting_strings, make_dirs_if_not_present=make_dirs)

        convert_snakes_to_json(
            parsed_snakes_to_json_settings["source_snakes_dir"],
            parsed_snakes_to_json_settings["target_json_dir"],
            parsed_snakes_to_json_settings["subdir_depth"],
            logger=logger
        )
    elif action_name == "join_sectioned_snakes":
        parsed_join_sectioned_snakes_settings = JoinSectionedSnakesSetupForm.parseSettings(setting_strings, make_dirs_if_not_present=make_dirs)

        join_sectioned_snakes(
            parsed_join_sectioned_snakes_settings["source_json_dir"],
            parsed_join_sectioned_snakes_settings["target_json_dir"],
            source_jsons_depth=parsed_join_sectioned_snakes_settings["source_jsons_depth"],
            logger=logger)
    elif action_name == "make_snake_images":
        parsed_make_snake_images_settings = MakeSnakeImagesSetupForm.parseSettings(setting_strings, make_dirs_if_not_present=make_dirs)

        make_snake_images(
            parsed_make_snake_images_settings["source_json_dir"],
            parsed_make_snake_images_settings["target_jpeg_dir"],
            parsed_make_snake_images_settings["width"],
            parsed_make_snake_images_settings["height"],
            parsed_make_snake_images_settings["snake_files_depth"],
            parsed_make_snake_images_settings["use_colors"],
            parsed_make_snake_images_settings["background_images_dir"],
            logger=logger,
        )
    elif action_name == "make_videos":
        parsed_make_snake_videos_settings = MakeSnakeVideosSetupForm.parseSettings(setting_strings, make_dirs_if_not_present=make_dirs)

        make_videos(
            parsed_make_snake_videos_settings["source_jpeg_dir"],
            parsed_make_snake_videos_settings["target_mp4_dir"],
            parsed_make_snake_videos_settings["source_images_depth"],
            logger=logger,
        )
    elif action_name == "make_orientation_fields":
        parsed_make_orientation_fields_settings = MakeOrientationFieldsSetupForm.parseSettings(setting_strings, make_dirs_if_not_present=make_dirs)

        make_orientation_fields(
            parsed_make_orientation_fields_settings["source_json_dir"],
            parsed_make_orientation_fields_settings["target_data_dir"],
            parsed_make_orientation_fields_settings["source_jsons_depth"],
            logger=logger,
        )
    else:
        raise Exception("Unknown action name '{}'".format(action_name))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Soax Helper')
    parser.add_argument('--load_settings',default=None,help="Skip GUI, Run from settings loaded from JSON file")
    parser.add_argument('--save_settings',default=None,help="Save settings from GUI menu to JSON file")
    parser.add_argument('--do_not_run', default=False, action='store_true', help='Will load or save settings but will not run. Use if you want to just create settings but not run them')
    parser.add_argument('--make_dirs',default=False,action='store_true', help='If --load_settings, whether program should make directories in settings file is the directories don\'t exist already.')

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
        app = SoaxSetupApp()
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

