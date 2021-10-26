import os
from snakeutils.logger import PrintLogger
from snakeutils.files import find_files_or_folders_at_depth
from snakeutils.snakejson import load_json_snakes

def make_field_for_json(json_fp, data_fp, logger):
    snakes_data, snakes_metadata = load_json_snakes(json_fp)

    raise NotImplementedError()

def make_orientation_fields(
    source_json_dir,
    target_data_dir,
    source_jsons_depth,
    image_width,
    image_height,
    logger=PrintLogger,
):
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