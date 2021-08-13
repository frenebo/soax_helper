from snakeutils.logger import PrintLogger
import json
import os
import numpy as np

def orientation_np_array_from_snakes(snakes, width, height, depth, snakes_are_3d, logger):
    if not snakes_are_3d:
        logger.FAIL("2D unsupported so far for CINDy matrices")

    if snakes_are_3d:
        orientation_arr = np.zeros((width, height, depth, 3, 3), dtype=np.float64)

def position_np_array_from_snakes(snakes, width, height, depth, snakes_are_3d, logger):
    if not snakes_are_3d:
        logger.FAIL("2D unsupported so far for CINDy matrices")

def cindy_matrices_from_snakes(
    source_json_dir,
    source_jsons_depth,
    width,
    height,
    depth,
    orientation_matrix_dir,
    position_matrix_dir,
    logger=PrintLogger,
    ):
    source_jsons_folders_and_filenames = find_files_or_folders_at_depth(source_json_dir,source_jsons_depth, ".json")

    for folder_path, snake_fn in source_jsons_folders_and_filenames:
        source_json_fp = os.path.join(folder_path, snake_fn)
        folder_relative_path = os.path.relpath(folder_path, source_json_dir)
        orientation_folder_path = os.path.join(orientation_matrix_dir, folder_relative_path)
        position_folder_path = os.path.join(position_matrix_dir, folder_relative_path)

        for target_folder_path in [orientation_folder_path, position_folder_path]:
            if not os.path.isdir(target_folder_path):
                if os.path.exists(target_folder_path):
                    logger.FAIL("Cannot output inside '{}', path exists but is not a directory".format(target_folder_path))
                else:
                    os.makedirs(target_folder_path)

        if snake_fn.startswith("3D"):
            snakes_are_3d = True
            if depth is None:
                logger.FAIL("Snake file '{}' is 3D, require depth parameter".format(source_json_fp))
        elif snake_fn.startswith("2D"):
            snakes_are_2d = False
        else:
            logger.FAIL("Could not determine if '{}' is 3D, filename does not start with '2D' or '3D'".format(source_json_fp))

        with open(source_json_fp, "r") as f:
            snakes = json.load(f)

        orientation_np_arr = orientation_np_array_from_snakes(
            snakes,
            width,
            height,
            depth,
            snakes_are_3d,
            logger,
        )

        position_np_arr = position_np_array_from_snakes(
            snakes,
            width,
            height,
            depth,
            snakes_are_3d,
            logger,
        )
