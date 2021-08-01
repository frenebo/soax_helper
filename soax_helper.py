from create_param_files import error_string_or_parse_arg_or_range
from preprocess_tiffs import preprocess_tiffs
from section_tiffs import section_tiffs
from create_param_files import create_param_files
from run_soax_with_params import run_soax_with_params
from snakeutils.logger import RecordLogger
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

    if app.do_preprocess:
        preprocess_logger = RecordLogger()

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

        parsed_sectioning_settings = SectioningSetupForm.parseSettings(app.sectioning_settings)

        section_tiffs(
            parsed_sectioning_settings["section_max_size"],
            parsed_sectioning_settings["source_tiff_dir"],
            parsed_sectioning_settings["target_sectioned_tiff_dir"],
            logger=sectioning_logger,
        )

    if app.do_create_params:
        create_params_logger = RecordLogger()

        parsed_param_settings = ParamsSetupForm.parseSettings(app.params_settings)
        create_param_files(
            parsed_params_settings["params_save_dir"],
            parsed_params_settings["alpha"],
            parsed_params_settings["beta"],
            parsed_params_settings["min_foreground"],
            parsed_params_settings["ridge_threshold"],
            logger=PrintLogger
        )

    if app.do_run_soax:
        soax_logger = RecordLogger()

        parsed_soax_settings = SoaxRunSetupForm.parseSettings(app.soax_run_settings)

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
        parsed_snakes_to_json_settings = SnakesToJsonSetupForm.parseSettings(app.snakes_to_json_settings)

        convert_snakes_to_json(
            parsed_snakes_to_json_settings["source_snakes_dir"],
            parsed_snakes_to_json_settings["target_json_dir"],
            parsed_snakes_to_json_settings["subdir_depth"],
            logger=snakes_to_json_logger
        )

    if app.do_join_sectioned_snakes:
        join_sectioned_snakes_logger = Record
        pass

    if app.do_make_snake_images:
        pass

    if app.do_make_videos_from_images:
        pass
