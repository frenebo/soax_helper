import os
import argparse
import json
import time

from .snakeutils.logger import FileLogger, RecordingLogger, ConsoleLogger, LoggerFAILCalledException
from .setup_app import (
    DivideAverageImageSetupForm,
    SoaxSetupApp,
    RescaleSetupForm,
    SectioningSetupForm,
    CreateNormalSoaxParamsSetupForm,
    CreateImageSpecificSoaxParamsSetupForm,
    SoaxParamsSetupPage1Form,
    SoaxParamsSetupPage2Form,
    SoaxParamsSetupPage3Form,
    SoaxRunSetupForm,
    SnakesToJsonSetupForm,
    JoinSectionedSnakesSetupForm,
    MakeSindyFieldsSetupForm,
    BeadPIVSetupForm,
)
from .tiff_info import tiff_info, tiff_file_or_dir_argparse_type

def parse_command_line_args_and_run():
    parser = argparse.ArgumentParser(description='Soax Helper')
    parser.add_argument('--load-settings',default=None,help="Skip GUI, Run from settings loaded from JSON file")
    parser.add_argument('--save-settings',default=None,help="Save settings from GUI menu to JSON file")
    parser.add_argument('--do-not-run', default=False, action='store_true', help='Will load or save settings but will not run. Use if you want to just create settings but not run them')
    parser.add_argument('--make-dirs',default=False,action='store_true', help='Whether helper should automatically create the configured directories if the directories don\'t exist already.')
    parser.add_argument('--save-logs-to-file', default=None,help='Text file to write soax helper output to')

    subparsers = parser.add_subparsers()
    subparsers.dest = 'subcommand'

    tiff_info_parser = subparsers.add_parser("tiffinfo", help="Get info from tiff file or directory of tiff files")
    tiff_info_parser.add_argument('target',type=tiff_file_or_dir_argparse_type,help="TIFF file or directory of tiff files")

    args = parser.parse_args()

    if args.subcommand is None:
        run_soax_helper(
            save_settings=args.save_settings,
            load_settings=args.load_settings,
            make_dirs=args.make_dirs,
            do_not_run=args.do_not_run,
            save_logs_to_file=args.save_logs_to_file,
        )
    elif args.subcommand == 'tiffinfo':
        tiff_info(args.target, logger=ConsoleLogger())

def run_soax_helper(save_settings, load_settings, make_dirs, do_not_run, save_logs_to_file)

    # Check if environment variable BATCH_SOAX_PATH is set for the path to the compiled
    # batch_soax executable, if not found use default value None
    batch_soax_path = os.getenv('BATCH_SOAX_PATH', None)

    if load_settings is not None and save_settings is not None:
        raise Exception("Loading settings and saving settings is not supported"
            "(loading tells program to skip GUI, but saving is meant to store "
            "settings configured in GUI)")
    if load_settings is not None:
        if notload_settings.endswith(".json"):
            raise Exception("Invalid settings load file '{}': must be json file".formatload_settings))

        if not os.path.existsload_settings):
            raise Exception("File '{}' does not exist".formatload_settings))

        with openload_settings, "r") as f:
            action_configs = json.load(f)
    else:
        if save_settings is not None:
            if not save_settings.endswith(".json"):
                raise Exception("Cannot save settings as '{}', file must have '.json' extension".format(save_settings))
            if os.path.exists(save_settings):
                raise Exception("Cannot save settings as '{}', already exists".format(save_settings))
        app = SoaxSetupApp(make_dirs=make_dirs, batch_soax_path=batch_soax_path)
        app.run()

        action_configs = app.getActionConfigs()

        if save_settings is not None:
            with open(save_settings, "w") as f:
                json.dump(action_configs, f, indent=4)

    if do_not_run:
        exit()

    console_logger = ConsoleLogger()

    if save_logs_to_file:
        with open(save_logs_to_file, 'w') as log_file:
            file_logger = FileLogger(log_filehandle=log_file, parent_logger=console_logger)
            run_actions(action_configs, make_dirs, logger=file_logger)
    else:
        run_actions(action_configs, make_dirs, logger=console_logger)

def run_actions(action_configs, make_dirs_if_not_present, logger):
    all_loggers = []
    all_times = []
    all_warnings = []

    for i, action_conf in enumerate(action_configs):
        action_name = action_conf["action"]
        action_settings = action_conf["settings"]

        start_time = time.time()

        action_logger = RecordingLogger(logger)
        all_loggers.append((action_name, action_logger))

        try:
            perform_action(action_name, action_settings, make_dirs_if_not_present, action_logger)
        except LoggerFAILCalledException as e:
            message = str(e)
            logger.error(message)

            end_time = time.time()
            elapsed = end_time - start_time
            logger.error("Step #{}, '{}' failed after {} seconds. Ending program".format(i + 1, action_name, elapsed))

            raise

        end_time = time.time()
        elapsed = end_time - start_time
        all_times.append((action_name, elapsed))
        logger.log("{} took {} seconds".format(action_name, elapsed))
        all_warnings.append(list(action_logger.warnings))


    for step_name, record_logger in all_loggers:
        if len(record_logger.errors) > 0:
            logger.error("ERRORS FROM {}".format(step_name))
            for err in record_logger.errors:
                logger.error("  " + err)

    for i, (step_name, seconds_taken) in enumerate(all_times):
        logger.log("Step #{}, '{}' took {} seconds".format(i + 1, step_name, seconds_taken))
        step_warnings = all_warnings[i]
        if len(step_warnings) > 0:
            logger.warn("    Step #{}, '{}' had the following warnings:".format(i + 1, step_name))
            for warning_text in step_warnings:
                logger.warn("        " + warning_text)

def perform_action(action_name, setting_strings, make_dirs, logger):
    from .rescale_tiffs import rescale_tiffs
    from .section_tiffs import section_tiffs
    from .run_soax import run_soax
    from .convert_snakes_to_json import convert_snakes_to_json
    from .join_sectioned_snakes import join_sectioned_snakes
    from .make_sindy_fields import make_sindy_fields
    from .bead_piv import bead_piv
    from .create_regular_soax_param_files import create_regular_soax_param_files
    from .create_image_specific_soax_param_files import create_image_specific_soax_param_files
    from .divide_average_image import divide_average_image

    if action_name == "divide_average_image":
        parsed_divide_average_image_settings = DivideAverageImageSetupForm.parseSettings(setting_strings, make_dirs)
        divide_average_image(
            parsed_divide_average_image_settings["source_tiff_dir"],
            parsed_divide_average_image_settings["target_tiff_dir"],
            logger=logger,
        )
    elif action_name == "rescale_tiffs":
        parsed_rescale_tiffs_settings = RescaleSetupForm.parseSettings(setting_strings, make_dirs)
        rescale_tiffs(
            parsed_rescale_tiffs_settings["source_tiff_dir"],
            parsed_rescale_tiffs_settings["target_tiff_dir"],
            parsed_rescale_tiffs_settings["input_dims"],
            parsed_rescale_tiffs_settings["output_dims"],
            parsed_rescale_tiffs_settings["workers_num"],
            logger=logger,
        )
    elif action_name == "section_tiffs":
        parsed_sectioning_settings = SectioningSetupForm.parseSettings(setting_strings, make_dirs)
        section_tiffs(
            parsed_sectioning_settings["section_max_size"],
            parsed_sectioning_settings["source_tiff_dir"],
            parsed_sectioning_settings["target_sectioned_tiff_dir"],
            parsed_sectioning_settings["workers_num"],
            logger=logger,
        )
    elif action_name == "create_regular_soax_param_files":
        create_normal_soax_param_files_settings = CreateNormalSoaxParamsSetupForm.parseSettings(setting_strings, make_dirs)
        param_field_strings = setting_strings["param_fields"]
        parsed_param_settings = {
            **SoaxParamsSetupPage1Form.parseSettings(param_field_strings, make_dirs),
            **SoaxParamsSetupPage2Form.parseSettings(param_field_strings, make_dirs),
            **SoaxParamsSetupPage3Form.parseSettings(param_field_strings, make_dirs),
        }
        create_regular_soax_param_files(
            params_save_dir=create_normal_soax_param_files_settings["params_save_dir"],
            param_settings=parsed_param_settings,
            logger=logger,
        )
    elif action_name == "create_image_specific_soax_param_files":
        create_image_specific_soax_param_files_settings = CreateImageSpecificSoaxParamsSetupForm.parseSettings(setting_strings, make_dirs)
        general_param_field_strings = setting_strings["general_param_fields"]
        parsed_general_param_settings = {
            **SoaxParamsSetupPage1Form.parseSettings(general_param_field_strings, make_dirs),
            **SoaxParamsSetupPage2Form.parseSettings(general_param_field_strings, make_dirs),
            **SoaxParamsSetupPage3Form.parseSettings(general_param_field_strings, make_dirs),
        }
        create_image_specific_soax_param_files(
            params_save_dir=create_image_specific_soax_param_files_settings["params_save_dir"],
            original_tiff_dir=create_image_specific_soax_param_files_settings["original_tiff_dir"],
            set_intensity_scaling_for_each_image=create_image_specific_soax_param_files_settings["set_intensity_scaling_for_each_image"],
            general_param_settings=parsed_general_param_settings,
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
            use_sectioned_images=parsed_soax_run_settings["use_sectioned_images"],
            use_image_specific_params=parsed_soax_run_settings["use_image_specific_params"],
            delete_soax_logs_for_finished_runs=parsed_soax_run_settings["delete_soax_logs_for_finished_runs"],
            workers_num=parsed_soax_run_settings["workers"],
            logger=logger,
        )
    elif action_name == "convert_snakes_to_json":
        parsed_snakes_to_json_settings = SnakesToJsonSetupForm.parseSettings(setting_strings, make_dirs)

        convert_snakes_to_json(
            parsed_snakes_to_json_settings["source_snakes_dir"],
            parsed_snakes_to_json_settings["target_json_dir"],
            parsed_snakes_to_json_settings["source_snakes_depth"],
            parsed_snakes_to_json_settings["offset_pixels"],
            parsed_snakes_to_json_settings["dims_pixels"],
            parsed_snakes_to_json_settings["pixel_spacing_um_xyz"],
            logger=logger,
        )
    elif action_name == "join_sectioned_snakes":
        parsed_join_sectioned_snakes_settings = JoinSectionedSnakesSetupForm.parseSettings(setting_strings, make_dirs)

        join_sectioned_snakes(
            parsed_join_sectioned_snakes_settings["source_json_dir"],
            parsed_join_sectioned_snakes_settings["target_json_dir"],
            parsed_join_sectioned_snakes_settings["source_jsons_depth"],
            parsed_join_sectioned_snakes_settings["workers"],
            logger=logger,
        )
    elif action_name == "make_sindy_fields":
        parsed_make_sindy_fields_settings = MakeSindyFieldsSetupForm.parseSettings(setting_strings, make_dirs)

        make_sindy_fields(
            parsed_make_sindy_fields_settings["source_images_dir"],
            parsed_make_sindy_fields_settings["source_json_dir"],
            parsed_make_sindy_fields_settings["save_orientations_dir"],
            parsed_make_sindy_fields_settings["save_intensities_dir"],
            parsed_make_sindy_fields_settings["source_jsons_depth"],
            logger=logger,
        )
    elif action_name == "do_bead_PIV":
        parsed_bead_PIV_settings = BeadPIVSetupForm.parseSettings(setting_strings, make_dirs)

        bead_piv(
            parsed_bead_PIV_settings["source_tiff_dir"],
            parsed_bead_PIV_settings["tiff_fn_letter_before_frame_num"],
            parsed_bead_PIV_settings["target_piv_data_dir"],
            parsed_bead_PIV_settings["x_y_pixel_size_um"],
            parsed_bead_PIV_settings["z_stack_spacing_um"],
            parsed_bead_PIV_settings["bead_diameter_um"],
            parsed_bead_PIV_settings["linking_search_range_um"],
            logger=logger,
        )
    else:
        raise Exception("Unknown action name '{}'".format(action_name))

if __name__ == "__main__":
    parse_command_line_args_and_run()
