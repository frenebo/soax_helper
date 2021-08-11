import sys
import os
import argparse
import numpy as np

def pil_img_3d_to_np_arr(pil_img):
    arr_3d = np.zeros((pil_img.height,pil_img.width,pil_img.n_frames),dtype=np.array(pil_img).dtype)
    for frame_idx in range(pil_img.n_frames):
        pil_img.seek(frame_idx)
        arr_3d[:,:, frame_idx] = np.array(pil_img)
    return arr_3d

def has_one_of_extensions(filename, file_extensions):
    for file_extension in file_extensions:
        if filename.lower().endswith(file_extension.lower()):
            return True
    return False

def find_files_or_folders_at_depth(source_dir_path, depth, file_extension=None, file_extensions=None, folders_not_files=False):
    if file_extensions is None and file_extension is None and not folders_not_files:
        raise Exception("If looking for a file, must ")

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

def run_fast_scandir(dir, ext):    # dir: str, ext: list
    subfolders, files = [], []

    for f in os.scandir(dir):
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in ext:
                files.append(f.path)


    for dir in list(subfolders):
        sf, f = run_fast_scandir(dir, ext)
        subfolders.extend(sf)
        files.extend(f)

    return subfolders, files

def extract_snakes(snake_file):
    # get past starting params
    count = 0
    while count < 30:
        snake_file.readline()
        count += 1

    snake_dict = {}
    done = False
    lines = [line.strip().split() for line in snake_file]

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
            #reached junction point section
            if len(line) == 3:
                break

            snake_name = line[0]
            snake_points = []

        if line_idx >= len(lines):
            end_of_snakes = True
        else:
            line = lines[line_idx]
            #reached junction section
            if len(line) == 3:
                end_of_snakes = True
            else:
                end_of_snakes = False

        if end_of_snakes:
            # save last snake and break loop
            snake_dict[snake_name] = snake_points
            break

        # if reached a new label for snake
        if len(line) == 1 :
            snake_dict[snake_name] = snake_points
            snake_name = None
            snake_points = None

            # skip open/closed #1 #0 line
            line_idx += 1

            # if this is the end of the snakes file now
            if line_idx >= len(lines):
                break

            continue
        # this number of items means s,p,x,y,fg_int,bg_int
        elif len(line) == 6:
            x = float(line[2])
            y = float(line[3])
            fg = float(line[4])
            bg = float(line[5])
            snake_points.append({"pos": [x,y], "fg": fg, "bg": bg})

            line_idx += 1
            continue
        # this number of items means s,p,x,y,z,fg_int,bg_int
        elif len(line) == 7:
            x = float(line[2])
            y = float(line[3])
            z = float(line[4])
            fg = float(line[5])
            bg = float(line[6])
            snake_points.append({"pos": [x,y,z], "fg": fg, "bg": bg})

            line_idx += 1
            continue
        else:
            raise Exception("Found line with {} items - unfamiliar number of line items. line:\n{}".format(len(line),line))

    snake_arr = []

    # turn dict into array of snakes starting at index zero
    for key in sorted(snake_dict.keys()):
        snake = snake_dict[key]
        snake_arr.append(snake)

    return snake_arr
