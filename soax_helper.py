from collections import OrderedDict

from create_param_files import error_string_or_parse_arg_or_range
from preprocess_tiffs import preprocess_tiffs
from section_tiffs import section_tiffs
from create_param_files import create_param_files
from run_soax_with_params import run_soax_with_params
from snakeutils.logger import RecordLogger
from convert_snakes_to_json import convert_snakes_to_json
from join_sectioned_snakes import join_sectioned_snakes
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

if __name__ == "__main__":
    app = SoaxSetupApp()
    app.run()

    all_loggers = OrderedDict()

    if app.do_preprocess:
        preprocess_logger = RecordLogger()
        all_loggers["PREPROCESS"] = preprocess_logger

        parsed_preprocess_settings = PreprocessSetupForm.parseSettings(app.preprocess_settings)

        preprocess_tiffs(
            parsed_preprocess_settings["source_tiff_dir"],
            parsed_preprocess_settings["target_tiff_dir"],
            parsed_preprocess_settings["max_cutoff_percent"],
            parsed_preprocess_settings["min_cutoff_percent"],
            logger=preprocess_logger,
        )

    if app.do_section:
        sectioning_logger = RecordLogger()
        all_loggers["SECTIONING"] = sectioning_logger

        parsed_sectioning_settings = SectioningSetupForm.parseSettings(app.sectioning_settings)

        section_tiffs(
            parsed_sectioning_settings["section_max_size"],
            parsed_sectioning_settings["source_tiff_dir"],
            parsed_sectioning_settings["target_sectioned_tiff_dir"],
            logger=sectioning_logger,
        )

    if app.do_create_params:
        create_params_logger = RecordLogger()
        all_loggers["CREATE PARAMS"] = create_params_logger

        parsed_params_settings = ParamsSetupForm.parseSettings(app.params_settings)
        create_param_files(
            parsed_params_settings["params_save_dir"],
            parsed_params_settings["alpha"],
            parsed_params_settings["beta"],
            parsed_params_settings["min_foreground"],
            parsed_params_settings["ridge_threshold"],
            logger=create_params_logger,
        )

    if app.do_run_soax:
        soax_logger = RecordLogger()
        all_loggers["RUN SOAX"] = soax_logger

        parsed_soax_run_settings = SoaxRunSetupForm.parseSettings(app.soax_run_settings)

        run_soax_with_params(
            parsed_soax_run_settings["batch_soax_path"],
            parsed_soax_run_settings["source_tiff_dir"],
            parsed_soax_run_settings["param_files_dir"],
            parsed_soax_run_settings["target_snakes_dir"],
            parsed_soax_run_settings["soax_log_dir"],
            parsed_soax_run_settings["use_subdirs"],
            parsed_soax_run_settings["workers"],
            logger=soax_logger)

    if app.do_snakes_to_json:
        snakes_to_json_logger = RecordLogger()
        all_loggers["SNAKES TO JSON"] = snakes_to_json_logger

        parsed_snakes_to_json_settings = SnakesToJsonSetupForm.parseSettings(app.snakes_to_json_settings)

        convert_snakes_to_json(
            parsed_snakes_to_json_settings["source_snakes_dir"],
            parsed_snakes_to_json_settings["target_json_dir"],
            parsed_snakes_to_json_settings["subdir_depth"],
            logger=snakes_to_json_logger
        )

    if app.do_join_sectioned_snakes:
        join_sectioned_snakes_logger = RecordLogger()
        all_loggers["JOIN SECTIONED SNAKES"] =join_sectioned_snakes_logger

        parsed_join_sectioned_snakes_settings = JoinSectionedSnakesSetupForm.parseSettings(app.join_sectioned_snakes_settings)

        join_sectioned_snakes(
            parsed_join_sectioned_snakes_settings["source_json_dir"],
            parsed_join_sectioned_snakes_settings["target_json_dir"],
            source_jsons_depth=parsed_join_sectioned_snakes_settings["source_jsons_depth"],
            logger=join_sectioned_snakes_logger)

    if app.do_make_snake_images:
        make_snake_images_logger = RecordLogger()
        all_loggers["MAKE SNAKE IMAGES"] = make_snake_images_logger

        make_snake_images(
            # parser = argparse.ArgumentParser(description='Try some parameters for snakes')
            # parser.add_argument('snake_dir',type=readable_dir,help="Source directory where snake text files are")
            # parser.add_argument('image_dir',type=readable_dir,help="Target directory to save graphed snakes")
            # parser.add_argument('--width',default=None,type=int,help="Width dimension of frame. Optional if can guess from image names")
            # parser.add_argument('--height',default=None,type=int,help="Width dimension of frame. Optional if can guess from image names")
            # parser.add_argument('--subdirs', default=False, action='store_true',help='If we should make snakes for subdirectories in snake_dir and output in subdirectories in image_dir')
            # parser.add_argument('--subsubdirs', default=False, action='store_true',help='If subdirectories in snake_dir are two levels deep')
            # parser.add_argument('-c','--colorful', action='store_true',help="Use different colors for each snake")
            # parser.add_argument('--background_img_dir', default=None,type=readable_dir,help="Directory with images to use as backgrounds for TIFs")
        )
        {
            "source_json_dir": "",
            "target_jpeg_dir": "./SnakeImages",
            "subdir_depth": "1",
        }

    if app.do_make_videos_from_images:
        make_videos_from_images = RecordLogger()
        all_loggers["MAKE VIDEOS"] = make_videos_from_images

    for step_name, record_logger in all_loggers.items():
        if len(record_logger.errors) > 0:
            PrintLogger.error("ERRORS FROM {}".format(step_name))
            for err in record_logger.errors:
                PrintLogger.error("  " + err)

