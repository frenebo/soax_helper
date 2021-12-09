import os

from .snakeutils.files import find_files_or_folders_at_depth, extract_snakes
from .snakeutils.logger import PrintLogger
from .snakeutils.snakejson import save_json_snakes

def infer_snakes_dims_and_offset_pixels(snake_filename):
    # remove "sec_" and ".txt"
    section_info_text = snake_filename[4:-4]
    x_bounds,y_bounds,z_bounds = section_info_text.split("_")
    # remove leading coordinate from bound string:
    # "x0100-0200" -> "0100-0200"
    x_bounds,y_bounds,z_bounds = x_bounds[1:],y_bounds[1:],z_bounds[1:]

    sec_x_lower,sec_x_upper = x_bounds.split("-")
    sec_y_lower,sec_y_upper = y_bounds.split("-")
    sec_z_lower,sec_z_upper = z_bounds.split("-")

    sec_x_lower = int(sec_x_lower)
    sec_x_upper = int(sec_x_upper)
    sec_y_lower = int(sec_y_lower)
    sec_y_upper = int(sec_y_upper)
    sec_z_lower = int(sec_z_lower)
    sec_z_upper = int(sec_z_upper)

    dims = [sec_x_upper - sec_x_lower, sec_y_upper - sec_y_lower, sec_z_upper - sec_z_lower]
    offset = [sec_x_lower, sec_y_lower, sec_z_lower]

    return dims, offset

def crop_snakes(orig_snake_list, lower_xyz, upper_xyz):
    new_snake_list = []
    for orig_snake in orig_snake_list:
        new_snake = []
        for orig_pt in orig_snake:
            orig_pos = orig_pt["pos"]
            fg = orig_pt["fg"]
            bg = orig_pt["bg"]

            new_pos = []
            # iterate over x,y,z
            for i in range(3):
                coord = orig_pos[i]
                if coord < lower_xyz[i]:
                    coord = lower_xyz[i]
                if coord > upper_xyz[i]:
                    coord = upper_xyz[i]
                new_pos.append(coord)

            new_pt = {
                "pos": new_pos,
                "fg": fg,
                "bg": bg,
            }
            new_snake.append(new_pt)
        new_snake_list.append(new_snake)
    return new_snake_list

def convert_snakes_to_json(
    source_snakes_dir,
    target_json_dir,
    source_snakes_depth,
    offset_pixels, # {"type": "infer"} or {"type": "int_coords", "value": [x,y,z]}
    dims_pixels, # {"type": "infer"} or {"type": "int_coords", "value": [0,0,0]}
    pixel_spacing_um_xyz, # [dx,dy,dz] pixel spacing in micrometers
    logger=PrintLogger):
    snakes_ext = ".txt"
    snake_folders_and_filenames = find_files_or_folders_at_depth(source_snakes_dir,source_snakes_depth,snakes_ext)

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

        json_fn = os.path.splitext(snake_filename)[0] + ".json"
        json_fp = os.path.join(target_folder_path, json_fn)

        if offset_pixels["type"] == "int_coords":
            offset_pixels_xyz = offset_pixels["value"]
        elif offset_pixels["type"] == "infer":
            __, offset_pixels_xyz = infer_snakes_dims_and_offset_pixels(snake_filename)
        else:
            raise Exception("Invalid type attribute in {}".format(offset_pixels))

        if dims_pixels["type"] == "int_coords":
            dims_pixels_xyz = dims_pixels["value"]
        elif dims_pixels["type"] == "infer":
            dims_pixels_xyz, __ = infer_snakes_dims_and_offset_pixels(snake_filename)
        else:
            raise Exception("Invalid type attribute in {}".format(dims_pixels))

        with open(snakes_fp) as f:
            snake_list = extract_snakes(f)
        # Occasionally SOAX may output snakes that leave the frame of the original image,
        # so we can limit the x,y,z coords of snake points to the dimensions of
        # the image section.
        snake_list = crop_snakes(snake_list, [0,0,0], dims_pixels_xyz)

        logger.log("  Writing JSON snakes to {}".format(json_fp))
        save_json_snakes(json_fp, snake_list, offset_pixels_xyz, dims_pixels_xyz, pixel_spacing_um_xyz)
