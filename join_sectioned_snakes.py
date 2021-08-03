from snakeutils.files import find_files_or_folders_at_depth
import os
import json
from snakeutils.logger import PrintLogger

# Given image slice dimensions, finds the highest width height (and depth if 3D) indices in names
# and retuns the width height and depth the orig image must have had
def get_section_bounds(fn, img_is_3d):
    # remove "xDsec_" and ".pickle"
    section_info = fn[6:-7]

    if img_is_3d:
        height_bounds,width_bounds,depth_bounds = section_info.split("_")
    else:
        height_bounds,width_bounds = section_info.split("_")

    sec_height_lower,sec_height_upper = height_bounds.split("-")
    sec_width_lower,sec_width_upper = width_bounds.split("-")
    if img_is_3d:
        sec_depth_lower,sec_depth_upper = depth_bounds.split("-")

    if img_is_3d:
        return sec_height_lower,sec_height_upper,sec_width_lower,sec_width_upper,sec_depth_lower,sec_depth_upper
    else:
        return sec_height_lower,sec_height_upper,sec_width_lower,sec_width_upper

def join_snake_files_and_save(source_dir, source_filenames, target_json_fp, logger):
    new_snakes = []
    if source_filepaths[0][:2] == "2D":
        are_3d = False
    elif source_filenames[0][:2] == "3D":
        are_3d = True
    else:
        logger.FAIL("Cannot join section {}, can't tell from filename if 2D or 3D".format(source_filenames[0]))

    shifted_snakes = []
    for snakes_fn in source_filenames:
        snakes_fp = os.path.join(source_dir, snakes_fn)
        with open(snakes_fp, "r") as f:
            section_snakes = json.load(f)

        sec_bounds = get_section_bounds(snakes_fn, are_3d)
        if are_3d:
            sec_height_lower,sec_height_upper,sec_width_lower,sec_width_upper,sec_depth_lower,sec_depth_upper = sec_bounds
        else:
            sec_height_lower,sec_height_upper,sec_width_lower,sec_width_upper = sec_bounds

        for snake in section_snakes:
            orig_pos = snake["pos"]
            if are_3d:
                shifted_pos = [
                    orig_pos[0] + sec_height_lower,
                    orig_pos[1] + sec_width_lower,
                    orig_pos[2] + sec_depth_lower,
                ]
            else:
                shifted_pos = [
                    orig_pos[0] + sec_height_lower,
                    orig_pos[1] + sec_width_lower
                ]

            shifted_snakes.append({
                "pos": shifted_pos,
                "fg": snake["fg"],
                "bg": snake["bg"],
            })

    with open(target_json_fp, "w") as f:
        json.dump(shifted_snakes, f)

def join_sectioned_snakes(source_json_dir, target_json_dir, source_jsons_depth,logger=PrintLogger):
    if source_jsons_depth < 1:
        raise Exception("Cannot join sectioned snakes if subdir depth is less than 1. Need a subdirectory full of sectioned snake jsons to produce one joined snake json in the target dir.")
    # The folders containing the source json files to be joined are one level less deep
    section_folder_depth = source_jsons_depth - 1
    source_folder_info = find_files_or_folders_at_depth(source_json_dir, section_folder_depth, folders_not_files=True)
    # info_strs = "    ".join(["({},{})".format(fol,fol2) for fol, fol2 in source_folder_info])
    # raise Exception("Source dir {}, target dir {}, depth {}, source info {}".format(source_json_dir, target_json_dir, section_folder_depth, info_strs))
    for containing_folder, source_folder_name in source_folder_info:

        relative_dir_path = os.path.relpath(containing_folder, source_json_dir)
        target_dir_path = os.path.join(target_json_dir, relative_dir_path)
        if not os.path.isdir(target_dir_path):
            if os.path.exists(target_dir_path):
                raise Exception("Cannot save results to {}, this exists but is not directory".format(target_dir_path))
            os.makedirs(target_dir_path)
        target_json_fp = os.path.join(target_dir_path, source_folder_name + ".json")

        source_folder_path = os.path.join(containing_folder, source_folder_name)
        source_files = [name for name in os.listdir(source_folder_path) if os.path.isfile(os.path.join(source_folder_info, name))]
        source_jsons = [fn for fn in source_files]
        source_jsons.sort()

        if len(source_jsons) == 0:
            logger.error("No JSON files found to join in {}".format(source_folder_path))
            continue

        join_snake_files_and_save(source_folder_path, source_jsons, target_json_fp)