import sys
import os
import numpy as np

def has_one_of_extensions(filename, file_extensions):
    for file_extension in file_extensions:
        if filename.lower().endswith(file_extension.lower()):
            return True
    return False

def find_tiffs_in_dir(dirpath):
    tiff_names = [filename for filename in os.listdir(dirpath) if has_one_of_extensions(filename, [".tif", ".tiff"])]
    tiff_names.sort()
    return tiff_names

def find_files_or_folders_at_depth(source_dir_path, depth, file_extension=None, file_extensions=None, folders_not_files=False):
    if file_extensions is None and file_extension is None and not folders_not_files:
        raise Exception("Bad function call, must specificy searching for folders, or specify file extension(s)")

    # if user provided one extension
    if (not folders_not_files) and file_extensions is None:
        file_extensions = [file_extension]
    contents = os.listdir(source_dir_path)
    contents.sort()

    if depth == 0:
        filenames = []
        dirnames = []
        for name in contents:
            if os.path.isdir(os.path.join(source_dir_path, name)):
                dirnames.append(name)
            elif os.path.isfile(os.path.join(source_dir_path, name)):
                filenames.append(name)

        if folders_not_files:
            folders_and_folders = [(source_dir_path, foldername) for foldername in dirnames]
            return folders_and_folders
        else:
            with_extension = [fn for fn in filenames if has_one_of_extensions(fn,file_extensions)]
            folders_and_files = [(source_dir_path, fn) for fn in with_extension]
            return folders_and_files
    # recursive find folders aand files at depth
    else:
        subdirs = [name for name in contents if os.path.isdir(os.path.join(source_dir_path,name))]
        folders_and_files = []
        for subdir_name in subdirs:
            sub_folders_and_files = find_files_or_folders_at_depth(
                os.path.join(source_dir_path,subdir_name),
                depth - 1,
                file_extension=file_extension,
                file_extensions=file_extensions,
                folders_not_files=folders_not_files)
            folders_and_files.extend(sub_folders_and_files)
        return folders_and_files

def extract_snakes(snake_file, logger=None):
    # get past starting params
    count = 0
    while count < 30:
        snake_file.readline()
        count += 1

    snake_dict = {}
    done = False
    lines = [line.rstrip() for line in snake_file.readlines()]
    if logger is not None:
        logger.log("Number of lines in snake file: {}".format(len(lines)))

    line_idx = 0
    snake_name = None
    snake_points = None
    while True:
        # if snake name is none, last iteration just finished a snake
        if snake_name is None:
            # nothing left in file
            if line_idx >= len(lines):
                break

            line = lines[line_idx]
            split_line = line.strip().split()
            #reached junction point section
            if len(split_line) == 3:
                break

            snake_name = line[0]
            snake_points = []

        if line_idx >= len(lines):
            end_of_snakes = True
        else:
            line = lines[line_idx]
            split_line = line.strip().split()
            #reached junction section
            if len(split_line) == 3:
                end_of_snakes = True
            else:
                end_of_snakes = False

        if end_of_snakes:
            # save last snake and break loop
            snake_dict[snake_name] = snake_points
            break

        # if reached a new label for snake
        if len(split_line) == 1 :
            snake_dict[snake_name] = snake_points
            snake_name = None
            snake_points = None

            # skip open/closed #1 #0 line
            line_idx += 1

            # if this is the end of the snakes file now
            if line_idx >= len(lines):
                break

            continue

        # Example line:
        #49           1     41.7002     55.7912     0.69079     49396.2     7611.91
        #snake number length is 2, since 49 has two digits. Each number after takes up
        #twelve columns
        try:
            snake_num_len = 0
            while line[snake_num_len] != ' ':
                snake_num_len += 1
            x_coord_start = snake_num_len + 12
            x_str = line[x_coord_start:x_coord_start + 12]
            y_str = line[x_coord_start + 12:x_coord_start + 12*2]
            z_str = line[x_coord_start + 12*2:x_coord_start + 12*3]
            fg_str = line[x_coord_start + 12*3:x_coord_start + 12*4]
            bg_str = line[x_coord_start + 12*4:x_coord_start + 12*5]

            x = float(x_str)
            y = float(y_str)
            z = float(z_str)
            fg = float(fg_str)
            bg = float(bg_str)
        except ValueError:
            raise

        snake_points.append({"pos": [x,y,z], "fg": fg, "bg": bg})
        line_idx += 1
        continue

    snake_arr = []

    # turn dict into array of snakes starting at index zero
    for key in sorted(snake_dict.keys()):
        snake = snake_dict[key]
        snake_arr.append(snake)

    return snake_arr
