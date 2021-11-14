import os
import numpy as np

from snakeutils.logger import PrintLogger
from snakeutils.files import find_files_or_folders_at_depth
from snakeutils.snakejson import load_json_snakes

def orientation_of_snake_pts(x, y, z, ds):
    pts = np.array( (x,y,z) )

    segment_diffs = pts[:,1:] - pts[:,0:-1]

    start_pt_orientation = segment_diffs[:,0]
    middle_pt_orientations = (segment_diffs[:,:-1] + segment_diffs[:,1:]) / 2
    end_pt_orientation = segment_diffs[:,-1]

    orient = np.zeros((3, len(x)))
    orient[:,0] = start_pt_orientation
    orient[:,1:-1] = middle_pt_orientations
    orient[:,-1] = end_pt_orientation

    return orient

def Qtensor(x, y, z, ds):
    nx, ny, nz = orientation_of_snake_pts(x, y, z, ds)
    Q = np.zeros((3, 3, len(x)))
    Q[0, 0, :] = nx*nx
    Q[1, 1, :] = ny*ny
    Q[2, 2, :] = nz*nz
    Q[0, 1, :] = nx*ny
    Q[0, 2, :] = nx*nz
    Q[1, 2, :] = ny*nz
    Q[1, 0, :] = Q[0, 1, :]
    Q[2, 0, :] = Q[0, 2, :]
    Q[2, 1, :] = Q[1, 2, :]
    return Q

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