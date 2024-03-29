import os
import argparse
import json
import time

from .snakeutils.logger import FileLogger, RecordingLogger, ConsoleLogger
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
    BeadPIVSetupForm,
    BeadLinkingSetupForm
)
from .utility_actions.tiff_info import tiff_info, tiff_file_or_dir_argparse_type
from .utility_actions.pad_tiff_numbers import pad_tiff_numbers
from .utility_actions.split_stacks import split_stacks

from .actions.bead_linking import link_beads
from .actions.bead_piv import bead_piv
from .actions.convert_snakes_to_json import convert_snakes_to_json
from .actions.create_regular_soax_param_files import create_regular_soax_param_files
from .actions.create_image_specific_soax_param_files import create_image_specific_soax_param_files
from .actions.divide_average_image import divide_average_image
from .actions.join_sectioned_snakes import join_sectioned_snakes
from .actions.rescale_tiffs import rescale_tiffs
from .actions.run_soax import run_soax
from .actions.section_tiffs import section_tiffs

def parse_command_line_args_and_run():
    parser = argparse.ArgumentParser(description='Soax Helper')

    subparsers = parser.add_subparsers()
    subparsers.dest = 'subcommand'
    subparsers.required = False

    config_parser = subparsers.add_parser("configure", help="Configure data processing settings, and save config as JSON file.")
    # run_parser.add_argument('--load-settings',default=None, help="Skip GUI, Run from settings loaded from JSON file")
    # run_parser.add_argument('--save-settings',default=None, help="Save settings from GUI menu to JSON file")
    # run_parser.add_argument('--do-not-run', default=False, action='store_true', help='Will load or save settings but will not run. Use if you want to just create settings but not run them')
    config_parser.add_argument("config_file", help="Name of JSON file to store configuration in")
    config_parser.add_argument('--auto-make-dirs',default=False, action='store_true', help='Use this if helper should automatically create the configured directories if the directories don\'t exist already.')
    # run_parser.add_argument('--save-logs', default=None, help='Specify text file to write soax helper output to')
    
    run_parser = subparsers.add_parser("run", help="Run data processing steps, as specified by a JSON config file (generated with soaxhelper configure)")
    run_parser.add_argument("config_file", help="Name of JSON file to load configuration from")
    run_parser.add_argument("--logfile", default=None, help="Log file to record the progress of data processing steps")
    # run_parser.add_argument('--auto-make-dirs',default=True, action='store_true', help='Automatically create directories if they don\'t exist already. ')
    

    tiff_info_parser = subparsers.add_parser("tiffinfo", help="Get info from tiff file or directory of tiff files")
    tiff_info_parser.add_argument('target',type=tiff_file_or_dir_argparse_type,help="TIFF file or directory of tiff files")

    pad_tiff_nums_parser = subparsers.add_parser("padtiffnums", help="In a directory, pad numbers in numbered tiff filenames. E.x. im1.tif, im10.tif, im300.tif become im001.tif, im010.tif, im300.tif")
    pad_tiff_nums_parser.add_argument("tiff_dir")
    pad_tiff_nums_parser.add_argument("tiff_name_prefix")
    pad_tiff_nums_parser.add_argument('--postfixlength',type=int, default=0)


    split_stacks_parser = subparsers.add_parser('splitstacks', help='Split 3D Tiffs into it 2D frames')
    split_stacks_parser.add_argument('source_tiff_dir')
    split_stacks_parser.add_argument('target_directory')
    
    args = parser.parse_args()
    
    if args.subcommand is None:
        parser.print_help()
    elif args.subcommand == 'configure':
        configure_soax_helper(
            config_filepath=args.config_file,
            create_missing_dirs_by_default=args.auto_make_dirs,
        )
    elif args.subcommand == "run":
        run_soax_helper(
            config_filepath=args.config_file,
            logfile=args.logfile,
        )
    elif args.subcommand == 'tiffinfo':
        tiff_info(args.target, logger=ConsoleLogger())
    elif args.subcommand == 'padtiffnums':
        pad_tiff_numbers(args.tiff_dir, args.tiff_name_prefix, postfix_length=args.postfixlength, logger=ConsoleLogger())
    elif args.subcommand == 'splitstacks':
        split_stacks(args.source_tiff_dir, args.target_directory,logger=ConsoleLogger())

    exit(0)
    

# @TODO - make sure to check before running whether ALL directories exist
# @TODO - move do_not_run functionality outside of this function!

def run_soax_helper(config_filepath, logfile=None):
    if not config_filepath.endswith(".json"):
        raise Exception("Invalid settings load file '{}': must be json file".format(config_filepath))

    if not os.path.exists(config_filepath):
        raise Exception("File '{}' does not exist".format(config_filepath))
        
    if logfile is not None:
        if os.path.exists(logfile):
            raise Exception("Cannot create logfile {}, already exists".format(logfile))
        

    with open(config_filepath, "r") as f:
        action_configs = json.load(f)
    

    if logfile is not None:
        with open(save_logs_to_file, 'w') as log_file:
            file_logger = FileLogger(log_filehandle=log_file, child_logger=console_logger)
            execute_data_actions(action_configs, True, logger=file_logger)
    else:
        execute_data_actions(action_configs, True, logger=console_logger)

def configure_soax_helper(config_filepath, create_missing_dirs_by_default=False):
    # Check if environment variable BATCH_SOAX_PATH is set for the path to the compiled
    # batch_soax executable, if not found use None, so SoaxSetupApp will ask user.
    batch_soax_path = os.getenv('BATCH_SOAX_PATH', None)

    if not config_filepath.endswith(".json"):
        raise Exception("Cannot save settings as '{}', file must have '.json' extension".format(config_filepath))
    if os.path.exists(config_filepath):
        raise Exception("Cannot save settings as '{}', already exists".format(config_filepath))
    
    with open(config_filepath, "w") as f:
        app = SoaxSetupApp(make_dirs=create_missing_dirs_by_default, batch_soax_path=batch_soax_path)
        app.run()

        action_configs = app.getActionConfigs()
    
        json.dump(action_configs, f, indent=4)
    
    print("Saved configuration in {}".format(config_filepath))

def execute_data_actions(action_configs, make_dirs_if_not_present, logger):
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
        except Exception as e:
            message = str(e)
            logger.error(message)

            end_time = time.time()
            elapsed = end_time - start_time
            logger.error("Step #{}, '{}' failed after {} seconds. Ending program".format(i + 1, action_name, elapsed))
            logger.error(message)

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
    elif action_name == "do_bead_PIV":
        parsed_bead_PIV_settings = BeadPIVSetupForm.parseSettings(setting_strings, make_dirs)

        bead_piv(
            source_tiff_dir=parsed_bead_PIV_settings["source_tiff_dir"],
            tiff_fn_letter_before_frame_num=parsed_bead_PIV_settings["tiff_fn_letter_before_frame_num"],
            tiff_fn_letter_before_z_num=parsed_bead_PIV_settings["tiff_fn_letter_before_z_num"],
            target_piv_data_dir=parsed_bead_PIV_settings["target_piv_data_dir"],
            brightness_threshold=parsed_bead_PIV_settings["brightness_threshold"],
            noise_size_xyz=parsed_bead_PIV_settings["noise_size_xyz"],
            bead_pixel_searchsize_xyz=parsed_bead_PIV_settings["bead_pixel_searchsize_xyz"],
            percentile=parsed_bead_PIV_settings["percentile"],
            processes=parsed_bead_PIV_settings["processes"],
            logger=logger,
        )
    elif action_name == "do_bead_linking":
        parsed_bead_linking_settings = BeadLinkingSetupForm.parseSettings(setting_strings, make_dirs)

        link_beads(
            pixel_spacing_um_xyz=parsed_bead_linking_settings["pixel_spacing_um_xyz"],
            linking_search_range_um=parsed_bead_linking_settings["linking_search_range_um"],
            source_piv_data_dir=parsed_bead_linking_settings["source_piv_data_dir"],
            target_linked_bead_data_dir=parsed_bead_linking_settings["target_linked_bead_data_dir"],
            logger=logger,
        )

    else:
        raise Exception("Unknown action name '{}'".format(action_name))

if __name__ == "__main__":
    parse_command_line_args_and_run()
