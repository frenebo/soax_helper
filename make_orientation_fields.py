import os
from snakeutils.logger import PrintLogger
from snakeutils.files import find_files_or_folders_at_depth

def make_field_for_json(json_fp, data_fp, logger):
    with open(json_fp, "r") as f:
        snakes_data = json.load(f)

    raise Exception("unimplemented")

def make_orientation_fields(source_json_dir, target_data_dir, source_jsons_depth, logger=PrintLogger):
    source_jsons_info = find_files_or_folders_at_depth(source_json_dir, source_jsons_depth, extension=".json")

    for json_containing_dirpath, json_filename in source_jsons_info:
        json_fp = os.path.join(json_containing_dirpath, json_filename)
        dir_relpath = os.path.relpath(json_containing_dirpath, source_json_dir)
        data_containing_dirpath = os.path.join(target_data_dir, dir_relpath)
        data_filename = json_fp[:-5] + ".npy"
        data_fp = os.path.join(data_containing_dirpath, data_filename)
        if not os.path.isdir(data_containing_dirpath):
            if os.path.exists(data_containing_dirpath):
                logger.FAIL("Cannot save orientation fields to {}, path exists but is not dir".format(data_containing_dirpath))
            else:
                os.makedirs(data_containing_dirpath)

        make_field_for_json(json_fp, data_fp, logger)