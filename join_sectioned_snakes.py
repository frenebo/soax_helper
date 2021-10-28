from snakeutils.files import find_files_or_folders_at_depth, has_one_of_extensions
import os
from multiprocessing.pool import ThreadPool
from snakeutils.logger import PrintLogger
from snakeutils.snakejson import load_json_snakes, save_json_snakes
from tiff_info import get_single_tiff_info

def join_snake_sections_folder_and_save(arg_dict):
    source_dir = arg_dict["source_dir"]
    source_filenames = arg_dict["source_filenames"]
    target_json_fp = arg_dict["target_json_fp"]
    logger = arg_dict["logger"]

    new_snakes = []

    shifted_snakes = []

    if len(source_filenames) == 0:
        logger.FAIL("Cannot join snake files, source dir '{}' contains no snake jsons.".format(sourcec_dir))

    # Make sure all sections have same units,
    # also keep track of size of the region that all of the sections cover
    first_sec_fp =  os.path.join(source_dir, source_filenames[0])
    __, first_sec_metadata = load_json_snakes(first_sec_fp)
    pixel_spacing_um_xyz = first_sec_metadata["pixel_spacing_um_xyz"]
    first_sec_dims_xyz = first_sec_metadata["dims_pixels_xyz"]
    first_sec_offset_pixels_xyz = first_sec_metadata["offset_pixels_xyz"]
    max_x = first_sec_dims_xyz[0] + first_sec_offset_pixels_xyz[0]
    max_y = first_sec_dims_xyz[1] + first_sec_offset_pixels_xyz[1]
    max_z = first_sec_dims_xyz[2] + first_sec_offset_pixels_xyz[2]

    for snakes_fn in source_filenames:
        snakes_fp = os.path.join(source_dir, snakes_fn)

        section_snakes, sec_metadata = load_json_snakes(snakes_fp)
        if sec_metadata["pixel_spacing_um_xyz"] != pixel_spacing_um_xyz:
            logger.FAIL("Pixel spacing ")

        sec_x_lower, sec_y_lower, sec_z_lower = sec_metadata["offset_pixels_xyz"]
        sec_dims = sec_metadata["dims_pixels_xyz"]
        sec_x_upper = sec_x_lower + sec_dims[0]
        sec_y_upper = sec_y_lower + sec_dims[1]
        sec_z_upper = sec_z_lower + sec_dims[2]
        if sec_x_upper > max_x:
            max_x = sec_x_upper
        if sec_y_upper > max_y:
            max_y = sec_y_upper
        if sec_z_upper > max_z:
            max_z = sec_z_upper

        for snake in section_snakes:
            shifted_snake = []
            for snake_part in snake:
                orig_pos = snake_part["pos"]

                shifted_pos = [
                    orig_pos[0] + sec_x_lower,
                    orig_pos[1] + sec_y_lower,
                    orig_pos[2] + sec_z_lower,
                ]

                shifted_snake.append({
                    "pos": shifted_pos,
                    "fg": snake_part["fg"],
                    "bg": snake_part["bg"],
                })
            shifted_snakes.append(shifted_snake)
    # We correct for the offset of all snake points, so the origin for snake coords is now
    # the origin of the original image
    pixels_offset = [0,0,0]
    dims_pixels_xyz = [max_x,max_y,max_z]

    save_json_snakes(target_json_fp, shifted_snakes, pixels_offset, dims_pixels_xyz, pixel_spacing_um_xyz)

def join_sectioned_snakes(
    source_json_dir,
    target_json_dir,
    source_jsons_depth,
    workers,
    logger=PrintLogger):
    if source_jsons_depth < 1:
        raise Exception("Cannot join sectioned snakes if subdir depth is less than 1. Need a subdirectory full of sectioned snake jsons to produce one joined snake json in the target dir.")
    # The folders containing the source json files to be joined are one level less deep
    section_folder_depth = source_jsons_depth - 1
    source_folder_info = find_files_or_folders_at_depth(source_json_dir, section_folder_depth, folders_not_files=True)

    join_sections_arg_dicts = []
    for containing_folder, source_folder_name in source_folder_info:

        relative_dir_path = os.path.relpath(containing_folder, source_json_dir)
        target_dir_path = os.path.join(target_json_dir, relative_dir_path)
        if not os.path.isdir(target_dir_path):
            if os.path.exists(target_dir_path):
                logger.FAIL("Cannot save results to {}, this exists but is not directory".format(target_dir_path))
            os.makedirs(target_dir_path)

        source_folder_path = os.path.join(containing_folder, source_folder_name)
        source_files = [name for name in os.listdir(source_folder_path) if os.path.isfile(os.path.join(source_folder_path, name))]
        source_jsons = [fn for fn in source_files if has_one_of_extensions(fn,[".json"])]
        source_jsons.sort()
        if len(source_jsons) == 0:
            logger.FAIL("No snake .json sections found in {}".format(source_folder_path))

        target_json_fn =source_folder_name + ".json"
        target_json_fp = os.path.join(target_dir_path, target_json_fn)

        join_sections_arg_dicts.append({
            "source_dir": source_folder_path,
            "source_filenames": source_jsons,
            "target_json_fp": target_json_fp,
            "logger": logger,
        })

    with ThreadPool(workers) as pool:
        future = pool.map(join_snake_sections_folder_and_save, join_sections_arg_dicts)
