from snakeutils.files import find_files_or_folders_at_depth, extract_snakes
import os
import json
from snakeutils.logger import PrintLogger

def join_snake_files_and_save(source_filepaths, target_json_fp, logger):
    new_snakes = []
    for snakes_fp in source_filepaths:
        with open(snake_fp, "r") as f:
            section_snakes = extract_snakes(f)
        for snake in section_snakes:
            raise Exception("UNIMPLEMENTE")

def join_sectioned_snakes(source_json_dir, target_json_dir, source_jsons_depth=1,logger=PrintLogger):
    if subdir_depth < 1:
        raise Exception("Cannot join sectioned snakes if subdir depth is less than 1. Need a subdirectory full of sectioned snake jsons to produce one joined snake json in the target dir.")
    # The folders containing the source json files to be joined are one level less deep
    section_folder_depth = source_jsons_depth - 1
    source_folder_info = find_files_or_folders_at_depth(source_json_dir, section_folder_depth, folders_not_files=True)
    for containing_folder, source_folder_name in source_folder_info:

        relative_dir_path = os.path.relpath(containing_folder, source_json_dir)
        target_dir_path = os.path.join(target_json_dir, relative_dir_path)
        if not os.path.isdir(target_dir_path):
            if os.path.exists(target_dir_path):
                raise Exception("Cannot save results to {}, this exists but is not directory".format(target_dir_path))
            os.makedirs(target_dir_path)
        target_json_fp = os.path.join(target_dir_path, source_folder_name + ".json")

        source_folder_path = os.path.join(containing_folder, source_folder_name)
        source_files = [name for name in os.listdir(source_folder_info) if os.path.isfile(of.path.join(source_folder_info, name))]
        source_json = [fn for fn in source_files]
        source_json.sort()

        join_snake_files_and_save(source_json, target_json_fp)