from snakeutils.logger import PrintLogger
import json
import os
import numpy as np
import math
import scipy.signal
# from skimage.draw import line_aa

def rasterize_line(start_coords, end_coords, arr_size):
    start_coords = np.array(start_coords)
    end_coords = np.array(end_coords)

    orig_x_diff = abs(end_coords[0] - start_coords[0])
    orig_y_diff = abs(end_coords[1] - start_coords[1])
    orig_z_diff = abs(end_coords[2] - start_coords[2])

    arr = np.zeros(arr_size,dtype=float)

    if orig_x_diff >= orig_y_diff and orig_x_diff >= orig_z_diff:
        primary_axis = 0
    elif orig_y_diff >= orig_z_diff:
        primary_axis = 1
    else:
        primary_axis = 2

    # make x-axis primary axis
    np.swapaxes(arr,0,primary_axis)
    start_coords[[0,primary_axis]] = start_coords[[primary_axis, 0]]
    end_coords[[0,primary_axis]] = end_coords[[primary_axis, 0]]

    x0 = start_coords[0]
    y0 = start_coords[1]
    z0 = start_coords[2]
    y_slope = (end_coords[1] - start_coords[1]) / (end_coords[0] - start_coords[0])
    z_slope = (end_coords[2] - start_coords[2]) / (end_coords[0] - start_coords[0])
    for x in range(start_coords[0], end_coords[0] + 1):
        y = int(y_slope * (x - x0))
        z = int(z_slope * (x - x0))
        arr[x,y,z] = 1

    # Swap x-axis back to whatever it was befor
    np.swapaxes(arr,0,primary_axis)
    start_coords[[0,primary_axis]] = start_coords[[primary_axis, 0]]
    end_coords[[0,primary_axis]] = end_coords[[primary_axis, 0]]

    return arr

def sphere_kernel_monochrome_arr(sphere_size):
    a = 1
    c = (3/5) * sphere_size

    kern  = np.zeros((sphere_size, sphere_size, sphere_size), dtype=float)
    center_pos = (sphere_size -  1)/2
    for i in range(sphere_size):
        for j in range(sphere_size):
            for k in range(sphere_size):
                dx = (i - center_pos)**2
                dy = (j - center_pos)**2
                dz = (k - center_pos)**2
                center_dist_squared = dx*dx + dy*dy + dz*dz
                point_val = a * math.exp(- center_dist_squared/ (2 * c * c))
                kern[i,j,k] = point_val

    return kern

# Expecting np.uint array shape (width, height, depth, 3)
def paint_vector_on_3D_arr_with_dyadic_vec_channel(
    arr,
    start_coords,
    end_coords,
    paint_matrix,
    kernel,
):
    kernel_size = kernel.shape[0]
    start_coords = np.array(start_coords)
    end_coords = np.array(end_coords)
    paint_matrix = np.array(paint_matrix)

    if paint_matrix.shape != (3,3):
        raise Exception("Expected paint matrix to be shape (3,3)")
    if kernel_size < 1:
        raise Exception("Kernel size is zero")
    if len(arr.shape) != 5:
        raise Exception("Unexpected array shape {}".format(str(arr.shape)))
    if arr.shape[-1] != 3:
        raise Exception("Expected arr shape to end with (3,3) for 3D dyadic tensor".format(vec_len=len(paint_vec)))
    if arr.shape[-2] != 3:
        raise Exception("Expected arr shape to end with (3,3) for 3D dyadic tensor".format(vec_len=len(paint_vec)))
    if arr.dtype != np.dtype('float64'):
        raise Exception("Expected array dtype float64")
    if len(kernel.shape) != 3:
        raise Exception("Expected 3D monochrome kernel")
    if kernel.dtype != np.dtype('float64'):
        raise Exception("Expected kernel dtype float64")

    line_low_corner = np.array([min(start_coords[i], end_coords[i]) for i in range(len(start_coords))], dtype=int)
    line_high_corner = np.array([max(start_coords[i], end_coords[i]) for i in range(len(start_coords))], dtype=int)

    # Making extra space around line segment so kernel has room. We could make window a bit smaller
    # but expanding each side by kernel_size to be safe
    window_low_corner = line_low_corner - np.array((kernel_size, kernel_size, kernel_size), dtype=int)
    window_high_corner = line_high_corner + np.array((kernel_size, kernel_size, kernel_size), dtype=int)
    # Cut off corners at image boundaries
    for i in range(3):
        if window_low_corner[i] < 0:
            window_low_corner[i] = 0
        if window_high_corner[i] >= arr.shape[i]:
            window_high_corner[i] = arr.shape[i] - 1

    window_shape = window_high_corner - window_low_corner
    # line_seg_shape = (abs(start_coords[0]))
    rasterized_line_seg = rasterize_line(start_coords - window_low_corner, end_coords - window_low_corner, window_shape)
    # shape (width, height, depth)
    convolved_line = scipy.signal.convolve(rasterized_line_seg, kernel, mode='same')
    # shape (width, height, depth, 3)
    matrix_convolved_line = np.multiply.outer(convolved_line, paint_matrix)

    print("ARR shape: {}".format(arr.shape))
    # print("rasterized shape")
    print("Convolved matrix shape: {}".format(matrix_convolved_line.shape))
    print("{}-{},    {}-{},     {}-{}".format(
        window_low_corner[0],window_high_corner[0],
        window_low_corner[1],window_high_corner[1],
        window_low_corner[2],window_high_corner[2],
    ))

    arr[
        window_low_corner[0]:window_high_corner[0],
        window_low_corner[1]:window_high_corner[1],
        window_low_corner[2]:window_high_corner[2],
    ] += matrix_convolved_line

def orientation_np_array_from_snakes(snakes, width, height, depth, snakes_are_3d, logger):
    if not snakes_are_3d:
        logger.FAIL("2D unsupported so far for CINDy matrices")

    if snakes_are_3d:
        orientation_vec_arr = np.zeros((width, height, depth, 3, 3), dtype=np.float64)
    else:
        orientation_vec_arr = np.zeros((width, height, 1, 3, 3), dtype=np.float64)

    kernel_size = 4
    kernel_3d = sphere_kernel_monochrome_arr(kernel_size)

    for snake in snakes:
        for seg_idx in range(len(snake) - 1):
            seg_start = snake[seg_idx]["pos"]
            seg_end = snake[seg_idx + 1]["pos"]

            # make 3d
            if len(seg_start) == 2:
                seg_start = seg_start + [0]
            if len(seg_end) == 2:
                seg_end = seg_end + [0]

            orientation_vec = np.array(seg_end, dtype=float) - np.array(seg_start, dtype=float)
            # normalize
            if np.dot(orientation_vec, orientation_vec) != 0:
                orientation_vec = orientation_vec / math.sqrt(np.dot(orientation_vec, orientation_vec))

            paint_vector_on_3D_arr_with_vec_channel(
                orientation_vec_arr,
                seg_start,
                seg_end,
                orientation_vec,
                kernel_3d,
            )

    return orientation_vec_arr


def position_np_array_from_snakes(snakes, width, height, depth, snakes_are_3d, logger):
    if not snakes_are_3d:
        logger.FAIL("2D unsupported so far for CINDy matrices")

def cindy_matrices_from_snakes(
    source_json_dir,
    source_jsons_depth,
    width,
    height,
    depth,
    orientation_matrix_dir,
    position_matrix_dir,
    logger=PrintLogger,
    ):
    source_jsons_folders_and_filenames = find_files_or_folders_at_depth(source_json_dir,source_jsons_depth, ".json")

    for folder_path, snake_fn in source_jsons_folders_and_filenames:
        source_json_fp = os.path.join(folder_path, snake_fn)
        folder_relative_path = os.path.relpath(folder_path, source_json_dir)
        orientation_folder_path = os.path.join(orientation_matrix_dir, folder_relative_path)
        position_folder_path = os.path.join(position_matrix_dir, folder_relative_path)

        for target_folder_path in [orientation_folder_path, position_folder_path]:
            if not os.path.isdir(target_folder_path):
                if os.path.exists(target_folder_path):
                    logger.FAIL("Cannot output inside '{}', path exists but is not a directory".format(target_folder_path))
                else:
                    os.makedirs(target_folder_path)

        if snake_fn.startswith("3D"):
            snakes_are_3d = True
            if depth is None:
                logger.FAIL("Snake file '{}' is 3D, require depth parameter".format(source_json_fp))
        elif snake_fn.startswith("2D"):
            snakes_are_2d = False
        else:
            logger.FAIL("Could not determine if '{}' is 3D, filename does not start with '2D' or '3D'".format(source_json_fp))

        with open(source_json_fp, "r") as f:
            snakes = json.load(f)

        orientation_np_arr = orientation_np_array_from_snakes(
            snakes,
            width,
            height,
            depth,
            snakes_are_3d,
            logger,
        )

        position_np_arr = position_np_array_from_snakes(
            snakes,
            width,
            height,
            depth,
            snakes_are_3d,
            logger,
        )
