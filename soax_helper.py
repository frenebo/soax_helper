from collections import OrderedDict
import os
import argparse
import json

from create_param_files import error_string_or_parse_arg_or_range
from preprocess_tiffs import preprocess_tiffs
from section_tiffs import section_tiffs
from create_param_files import create_param_files
from run_soax import run_soax
from snakeutils.logger import RecordLogger, PrintLogger
from convert_snakes_to_json import convert_snakes_to_json
from join_sectioned_snakes import join_sectioned_snakes
from make_snake_images import make_snake_images
from make_videos import make_videos

from setup_app import (
    SoaxSetupApp,
    PreprocessSetupForm,
    SectioningSetupForm,
    ParamsSetupForm,
    SoaxRunSetupForm,
    SnakesToJsonSetupForm,
    JoinSectionedSnakesSetupForm,
    MakeSnakeImagesSetupForm,
    MakeSnakeVideosSetupForm,
)

def perform_action(action_name, setting_strings, logger):
    if action_name == "preprocess_tiffs":
        parsed_preprocess_settings = PreprocessSetupForm.parseSettings(setting_strings)
        preprocess_tiffs(
            parsed_preprocess_settings["source_tiff_dir"],
            parsed_preprocess_settings["target_tiff_dir"],
            parsed_preprocess_settings["max_cutoff_percent"],
            parsed_preprocess_settings["min_cutoff_percent"],
            logger=logger,
        )
    elif action_name == "section_tiffs":
        parsed_sectioning_settings = SectioningSetupForm.parseSettings(setting_strings)
        section_tiffs(
            parsed_sectioning_settings["section_max_size"],
            parsed_sectioning_settings["source_tiff_dir"],
            parsed_sectioning_settings["target_sectioned_tiff_dir"],
            logger=logger,
        )
    elif action_name == "create_param_files":
        parsed_params_settings = ParamsSetupForm.parseSettings(setting_strings)
        create_param_files(
            parsed_params_settings["params_save_dir"],
            parsed_params_settings["alpha"],
            parsed_params_settings["beta"],
            parsed_params_settings["min_foreground"],
            parsed_params_settings["ridge_threshold"],
            logger=logger,
        )
    elif action_name == "run_soax":
        parsed_soax_run_settings = SoaxRunSetupForm.parseSettings(setting_stings)

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
        parsed_snakes_to_json_settings = SnakesToJsonSetupForm.parseSettings(setting_strings)

        convert_snakes_to_json(
            parsed_snakes_to_json_settings["source_snakes_dir"],
            parsed_snakes_to_json_settings["target_json_dir"],
            parsed_snakes_to_json_settings["subdir_depth"],
            logger=logger
        )
    elif action_name == "join_sectioned_snakes":
        parsed_join_sectioned_snakes_settings = JoinSectionedSnakesSetupForm.parseSettings(setting_strings)

        join_sectioned_snakes(
            parsed_join_sectioned_snakes_settings["source_json_dir"],
            parsed_join_sectioned_snakes_settings["target_json_dir"],
            source_jsons_depth=parsed_join_sectioned_snakes_settings["source_jsons_depth"],
            logger=logger)
    elif action_name == "make_snake_images":
        parsed_make_snake_images_settings = MakeSnakeImagesSetupForm.parseSettings(setting_strings)

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
        parsed_make_snake_videos_settings = MakeSnakeVideosSetupForm.parseSettings(setting_strings)

        make_videos(
            parsed_make_snake_videos_settings["source_jpeg_dir"],
            parsed_make_snake_videos_settings["target_mp4_dir"],
            parsed_make_snake_videos_settings["source_images_depth"],
            logger=logger,
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Soax Helper')
    parser.add_argument('--load_settings',default=None,help="Skip GUI, Run from settings loaded from JSON file")
    parser.add_argument('--save_settings',default=None,help="Save settings from GUI menu to JSON file")
    parser.add_argument('--do_not_run', default=False, action='store_true', help='Will load or save settings but will not run. Use if you want to just create settings but not run them')

    args = parser.parse_args()
    if args.load_settings is not None and args.save_settings is not None:
        raise Exception("Loading settings and saving settings is not supported"
            "(loading tells program to skip GUI, but saving is meant to store "
            "settings configured in GUI)")
    if args.load_settings is not None:
        if not args.load_settings.endswith(".json"):
            raise Exception("Invalid settings load file '{}': must be json file".format(args.load_settings))

        if not os.file.exists(args.load_settings):
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

    all_loggers = OrderedDict()

    for action_conf in action_configs:
        action_name = action_conf["action"]
        action_settings = action_conf["settings"]

        action_logger = RecordLogger()
        all_loggers[action_name] = action_logger

        perform_action(action_name, action_settings, action_logger)

    for step_name, record_logger in all_loggers.items():
        if len(record_logger.errors) > 0:
            PrintLogger.error("ERRORS FROM {}".format(step_name))
            for err in record_logger.errors:
                PrintLogger.error("  " + err)

