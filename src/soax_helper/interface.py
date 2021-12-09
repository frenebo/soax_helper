import os
import argparse
import json
import time

from .snakeutils.logger import RecordLogger, PrintLogger, LoggerFAILCalledException
from .setup_app import (
    DivideAverageImageSetupForm,
    SoaxSetupApp,
    RescaleSetupForm,
    SectioningSetupForm,
    SoaxParamsSetupPage1Form,
    SoaxParamsSetupPage2Form,
    SoaxParamsSetupPage3Form,
    SoaxRunSetupForm,
    SnakesToJsonSetupForm,
    JoinSectionedSnakesSetupForm,
    MakeSindyFieldsSetupForm,
    BeadPIVSetupForm,
)

def perform_action(action_name, setting_strings, make_dirs, logger):
    from .rescale_tiffs import rescale_tiffs
    from .section_tiffs import section_tiffs
    from .run_soax import run_soax
    from .convert_snakes_to_json import convert_snakes_to_json
    from .join_sectioned_snakes import join_sectioned_snakes
    from .make_sindy_fields import make_sindy_fields
    from .bead_piv import bead_piv
    from .tube_piv import tube_piv
    from .create_regular_soax_param_files import create_regular_soax_param_files
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
        param_fields = setting_strings["param_fields"]
        parsed_param_settings = {
            **SoaxParamsSetupPage1Form.parseSettings(param_fields, make_dirs),
            **SoaxParamsSetupPage2Form.parseSettings(param_fields, make_dirs),
            **SoaxParamsSetupPage3Form.parseSettings(param_fields, make_dirs),
        }
        create_regular_soax_param_files(
            params_save_dir=setting_strings["params_save_dir"],
            param_settings=parsed_param_settings,
            logger=logger,
        )
    elif action_name == "create_image_image_specific_params_files":
        param_fields = setting_strings["param_fields"]
        parsed_param_settings = {
            **SoaxParamsSetupPage1Form.parseSettings(param_fields, make_dirs),
            **SoaxParamsSetupPage2Form.parseSettings(param_fields, make_dirs),
            **SoaxParamsSetupPage3Form.parseSettings(param_fields, make_dirs),
        }
        #@TODO
        raise NotImplementedError()
    # elif action_name == "create_soax_param_files":
    #     parsed_page1_params_settings = SoaxParamsSetupPage1Form.parseSettings(setting_strings, make_dirs)
    #     parsed_page2_params_settings = SoaxParamsSetupPage2Form.parseSettings(setting_strings, make_dirs)
    #     parsed_page3_params_settings = SoaxParamsSetupPage3Form.parseSettings(setting_strings, make_dirs)

    #     parsed_params_settings = {
    #         **parsed_page1_params_settings,
    #         **parsed_page2_params_settings,
    #         **parsed_page3_params_settings,
    #     }

    #     create_soax_param_files(
    #         target_dir=parsed_params_settings["params_save_dir"],
    #         init_z=parsed_params_settings["init_z"],
    #         damp_z=parsed_params_settings["damp_z"],
    #         intensity_scaling_start_stop_step=parsed_params_settings["intensity_scaling"],
    #         gaussian_std_start_stop_step=parsed_params_settings["gaussian_std"],
    #         ridge_threshold_start_stop_step=parsed_params_settings["ridge_threshold"],
    #         maximum_foreground_start_stop_step=parsed_params_settings["maximum_foreground"],
    #         minimum_foreground_start_stop_step=parsed_params_settings["minimum_foreground"],
    #         snake_point_spacing_start_stop_step=parsed_params_settings["snake_point_spacing"],
    #         min_snake_length_start_stop_step=parsed_params_settings["min_snake_length"],
    #         maximum_iterations_start_stop_step=parsed_params_settings["maximum_iterations"],
    #         change_threshold_start_stop_step=parsed_params_settings["change_threshold"],
    #         check_period_start_stop_step=parsed_params_settings["check_period"],
    #         alpha_start_stop_step=parsed_params_settings["alpha"],
    #         beta_start_stop_step=parsed_params_settings["beta"],
    #         gamma_start_stop_step=parsed_params_settings["gamma"],
    #         external_factor_start_stop_step=parsed_params_settings["external_factor"],
    #         stretch_factor_start_stop_step=parsed_params_settings["stretch_factor"],
    #         number_of_background_radial_sectors_start_stop_step=parsed_params_settings["number_of_background_radial_sectors"],
    #         background_z_xy_ratio_start_stop_step=parsed_params_settings["background_z_xy_ratio"],
    #         radial_near_start_stop_step=parsed_params_settings["radial_near"],
    #         radial_far_start_stop_step=parsed_params_settings["radial_far"],
    #         delta_start_stop_step=parsed_params_settings["delta"],
    #         overlap_threshold_start_stop_step=parsed_params_settings["overlap_threshold"],
    #         grouping_distance_threshold_start_stop_step=parsed_params_settings["grouping_distance_threshold"],
    #         grouping_delta_start_stop_step=parsed_params_settings["grouping_delta"],
    #         minimum_angle_for_soac_linking_start_stop_step=parsed_params_settings["minimum_angle_for_soac_linking"],
    #         logger=logger,
    #     )
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
    elif action_name == "do_tube_PIV":
        parsed_tube_PIV_settings = TubePIVSetupForm.parseSettings(setting_strings, make_dirs)

        tube_piv(
            parsed_tube_PIV_settings["source_tiff_dir"],
            parsed_tube_PIV_settings["target_piv_data_dir"],
            logger=logger,
        )
    else:
        raise Exception("Unknown action name '{}'".format(action_name))

def parse_command_line_args_and_run():
    parser = argparse.ArgumentParser(description='Soax Helper')
    parser.add_argument('--load-settings',default=None,help="Skip GUI, Run from settings loaded from JSON file")
    parser.add_argument('--save-settings',default=None,help="Save settings from GUI menu to JSON file")
    parser.add_argument('--do-not-run', default=False, action='store_true', help='Will load or save settings but will not run. Use if you want to just create settings but not run them')
    parser.add_argument('--make-dirs',default=False,action='store_true', help='Whether helper should automatically create the configured directories if the directories don\'t exist already.')

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
    all_warnings = []

    for i, action_conf in enumerate(action_configs):
        action_name = action_conf["action"]
        action_settings = action_conf["settings"]

        start_time = time.time()

        action_logger = RecordLogger()
        all_loggers.append((action_name, action_logger))

        try:
            perform_action(action_name, action_settings, args.make_dirs, action_logger)
        except LoggerFAILCalledException as e:
            message = str(e)
            PrintLogger.error(message)

            end_time = time.time()
            elapsed = end_time - start_time
            PrintLogger.error("Step #{}, '{}' failed after {} seconds. Ending program".format(i + 1, action_name, elapsed))
            exit(1)

        end_time = time.time()
        elapsed = end_time - start_time
        all_times.append((action_name, elapsed))
        PrintLogger.log("{} took {} seconds".format(action_name, elapsed))
        all_warnings.append(list(action_logger.warnings))


    for step_name, record_logger in all_loggers:
        if len(record_logger.errors) > 0:
            PrintLogger.error("ERRORS FROM {}".format(step_name))
            for err in record_logger.errors:
                PrintLogger.error("  " + err)

    for i, (step_name, seconds_taken) in enumerate(all_times):
        PrintLogger.log("Step #{}, '{}' took {} seconds".format(i + 1, step_name, seconds_taken))
        step_warnings = all_warnings[i]
        if len(step_warnings) > 0:
            PrintLogger.warn("    Step #{}, '{}' had the following warnings:".format(i + 1, step_name))
            for warning_text in step_warnings:
                PrintLogger.warn("        " + warning_text)


if __name__ == "__main__":
    parse_command_line_args_and_run()
