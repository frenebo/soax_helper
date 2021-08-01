from snakeutils.files import get_folders_and_files_at_subdir_depth, extract_snakes
import os
import json
from snakeutils.logger import PrintLogger

def convert_snakes_to_json(source_snakes_dir, target_json_dir, subdir_depth=0, logger=PrintLogger):
    snakes_ext = ".txt"
    snake_folders_and_filenames = get_folders_and_files_at_subdir_depth(source_snakes_dir,subdir_depth,snakes_ext)

    for folder_path, snake_filename in snake_folders_and_filenames:
        folder_relative_path = os.path.relpath(folder_path, source_snakes_dir)
        target_folder_path = os.path.join(target_json_dir, folder_relative_path)
        if not os.path.isdir(target_folder_path):
            if os.path.exists(target_folder_path):
                raise Exception("Cannot produce output, {} is not a directory".format(target_folder_path))
            else:
                os.makedirs(target_folder_path)
        snakes_fp = os.path.join(folder_path,snake_filename)
        logger.log("Reading snakes from {}".format(snakes_fp))

        with open(snakes_fp) as f:
            snakes = extract_snakes(f)

        json_str = json.dumps(snakes)

        json_fn = snake_filename[:-len(snakes_ext)] + ".json"
        json_fp = os.path.join(target_folder_path, json_fn)
        logger.log("  Writing JSON snakes to {}".format(json_fp))
        with open(json_fp, 'w') as f:
            f.write(json_str)

