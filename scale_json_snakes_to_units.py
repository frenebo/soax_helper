from snakeutils.files import find_files_or_folders_at_depth
from snakeutils.logger import PrintLogger
from snakeutils.snakejson import load_json_snakes, save_json_snakes
import os

def rescale_json_snake_file(
    source_json_fp,
    target_json_fp,
    x_y_pixel_size_um,
    x_y_image_scale_factor,
    z_stack_spacing_um,
    logger,
):
    orig_snakes = load_json_snakes(source_json_fp)

    rescaled_snakes = []
    for orig_snake in orig_snakes:
        rescaled_snake = []
        for orig_snake_part in orig_snake:
            orig_pos = orig_snake["pos"]
            rescaled_pos = [
                orig_pos[0] * x_y_pixel_size_um / x_y_image_scale_factor,
                orig_pos[1] * x_y_pixel_size_um / x_y_image_scale_factor,
                orig_pos[2] * z_stack_spacing_um,
            ]
            rescaled_snake.append({
                "pos": rescaled_pos,
                "fg": orig_snake_part["fg"],
                "bg": orig_snake_part["bg"],
            })
        rescaled_snakes.append(rescaled_snake)

    save_json_snakes(target_json_fp, rescaled_snakes)

def scale_json_snakes_to_units(
    source_json_dir,
    source_jsons_depth,
    target_json_dir,
    x_y_pixel_size_um,
    x_y_image_scale_factor,
    z_stack_spacing_um,
    unit_abbreviation,
    logger=PrintLogger,
    ):
    source_jsons_folders_and_filenames = find_files_or_folders_at_depth(source_json_dir,source_jsons_depth, ".json")

    for folder_path, snake_fn in source_jsons_folders_and_filenames:
        folder_relative_path = os.path.relpath(folder_path, source_json_dir)
        target_folder_path = os.path.join(target_json_dir, folder_relative_path)
        if not os.path.isdir(target_folder_path):
            if os.path.exists(target_folder_path):
                logger.FAIL("Cannot output inside '{}', path exists but is not directory".format(target_folder_path))
            else:
                os.makedirs(target_folder_path)
        target_snake_fn = "units_" + unit_abbreviation + "_" + snake_fn
        source_json_fp = os.path.join(folder_path, snake_fn)
        target_json_fp = os.path.join(target_folder_path, target_snake_fn)

        rescale_json_snake_file(
            source_json_fp,
            target_json_fp,
            x_y_pixel_size_um,
            x_y_image_scale_factor,
            z_stack_spacing_um,
            logger,
        )
