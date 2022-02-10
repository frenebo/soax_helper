import os
import numpy as np
import csv
from PIL import Image
from scipy.sparse import save_npz, coo_matrix
from scipy.integrate import odeint, cumtrapz
from scipy.interpolate import splrep, splder, splev
import scipy.optimize as optimize
from scipy.interpolate import UnivariateSpline
import math

from .snakeutils.files import find_files_or_folders_at_depth, has_one_of_extensions, find_tiffs_in_dir
from .snakeutils.snakejson import load_json_snakes
from .snakeutils.tifimage import open_tiff_as_np_arr, save_3d_tif

intensity_field_around_snake_radius_pixels = 5

def bresenham_line_pts(start_coords, end_coords):
    x_start,y_start,z_start = start_coords
    x_end,y_end,z_end = end_coords
    x_start,y_start,z_start = int(x_start),int(y_start),int(z_start)
    x_end,y_end,z_end = int(x_end),int(y_end),int(z_end)

    points = [ (x_start,y_start,z_start) ]

    x, y, z = x_start,y_start,z_start

    dx = abs(x_end - x_start)
    dy = abs(y_end - y_start)
    dz = abs(z_end - z_start)

    xs = 1 if x_end > x_start else -1
    ys = 1 if y_end > y_start else -1
    zs = 1 if z_end > z_start else -1

    # Driving axis X
    if (dx >= dy and dx >= dz):
        p1 = 2 * dy - dx
        p2 = 2 * dz - dx
        while (x != x_end):
            x += xs
            if (p1 >= 0):
                y += ys
                p1 -= 2 * dx
            if (p2 >= 0):
                z += zs
                p2 -= 2 * dx
            p1 += 2 * dy
            p2 += 2 * dz
            points.append( (x, y, z) )

    # Driving axis Y
    elif (dy >= dx and dy >= dz):
        p1 = 2 * dx - dy
        p2 = 2 * dz - dy
        while (y != y_end):
            y += ys
            if (p1 >= 0):
                x += xs
                p1 -= 2 * dy
            if (p2 >= 0):
                z += zs
                p2 -= 2 * dy
            p1 += 2 * dx
            p2 += 2 * dz
            points.append((x, y, z))

    # Driving axis Z
    else:
        p1 = 2 * dy - dz
        p2 = 2 * dx - dz
        while (z != z_end):
            z += zs
            if (p1 >= 0):
                y += ys
                p1 -= 2 * dz
            if (p2 >= 0):
                x += xs
                p2 -= 2 * dz
            p1 += 2 * dy
            p2 += 2 * dx
            points.append((x, y, z))
    return np.array(points).T

def get_snake_path_parametric(x,y,z):
    length = np.sum(np.sqrt(np.diff(np.asarray(z))**2+np.diff(np.asarray(y))**2+np.diff(np.asarray(x))**2))
    spl_x = UnivariateSpline(l, x)
    spl_x.set_smoothing_factor(0)
    spl_y = UnivariateSpline(l, y)
    spl_y.set_smoothing_factor(0)
    spl_z = UnivariateSpline(l, z)
    spl_z.set_smoothing_factor(0)

    return spl_x, spl_y, spl_z, length

def orientation_of_snake_segments(snake_pts):
    orient = snake_pts[:,1:] - snake_pts[:,0:-1]
    orient = orient/np.sqrt(orient[0, :]**2 + orient[1, :]**2+ orient[2, :]**2)

    return orient

def Qtensor(orientation_unit_vectors):
    nx, ny, nz = orientation_unit_vectors

    Q = np.zeros((3, 3, len(nx)))
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

def get_json_snake_xyz(snake):
    X = []
    Y = []
    Z = []
    for pt in snake:
        x,y,z = pt["pos"]
        X.append(x)
        Y.append(y)
        Z.append(z)
    return np.array((X,Y,Z))

# Sometimes snakes go outside, >= the dimensions of the box. This "crops" the points
def snakes_limit_to_dims(snakes, dims):
    for snake in snakes:
        for pt in snake:
            if pt["pos"][0] >= dims[0]:
                pt["pos"][0] = dims[0] - 1
            if pt["pos"][1] >= dims[1]:
                pt["pos"][1] = dims[1] - 1
            if pt["pos"][2] >= dims[2]:
                pt["pos"][2] = dims[2] - 1

def save_intensity_csv(arr, fp):
    with open(fp, "w", newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["x", "y", "z", "intensity"])
        non_zero_indices = np.argwhere(arr != 0)
        for x, y, z in non_zero_indices:
            writer.writerow([str(x),str(y),str(z),str(arr[x,y,z])])
    #     spamwriter = csv.writer(csvfile, delimiter=' ',
    #                         quotechar='|', quoting=csv.QUOTE_MINIMAL)
    # spamwriter.writerow(['Spam'] * 5 + ['Baked Beans'])
    # spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])

# def save_orientation_csv(arr, fp):


def make_fields(
    json_fp,
    image_fp,
    orientation_fp,
    intensities_fp,
    logger):
    snakes, metadata = load_json_snakes(json_fp)
    image_dims = metadata["dims_pixels_xyz"]
    snakes_limit_to_dims(snakes, image_dims)

    unswapped_np_image = open_tiff_as_np_arr(image_fp)
    # From Y,X,Z to X,Y,Z
    xyz_np_image = np.swapaxes(unswapped_np_image, 0, 1)

    Qtensor_arr = np.zeros(image_dims + [3,3,3], dtype=float)
    snake_exists_arr = np.zeros(image_dims, dtype=float)
    min_x = snakes[0][0]["pos"][0]
    min_y = snakes[0][0]["pos"][1]
    min_z = snakes[0][0]["pos"][2]
    max_x = min_x
    max_y = min_y
    max_z = min_z
    logger.log("Making orientation and intensity fiels for {}".format(json_fp))
    for snake in snakes:
        snake_pts = get_json_snake_xyz(snake)
        interval_orientations = orientation_of_snake_segments(snake_pts)
        interval_Qtensors = Qtensor(interval_orientations)

        for interval_idx in range(snake_pts.shape[1] - 1):
            interval_Q = interval_Qtensors[:,:,interval_idx]
            start_pt = snake_pts[:,interval_idx]
            end_pt = snake_pts[:,interval_idx + 1]

            pts_on_interval = bresenham_line_pts(start_pt,end_pt)

            x_coords, y_coords, z_coords = pts_on_interval

            Qtensor_arr[x_coords, y_coords, z_coords] = interval_Q
            snake_exists_arr[x_coords, y_coords, z_coords] = 1.0
    # np.multiply(np_image, snake_exists_arr)
    if xyz_np_image.shape != snake_exists_arr.shape:
        raise Exception("Image shape not same as snake exists arr: {} vs {}".format(np_image.shape, snake_exists_arr.shape))
    intensity_arr = np.multiply(xyz_np_image, snake_exists_arr)

    logger.log("    Saving orientations to {}. Size {}".format(orientation_fp, Qtensor_arr.shape))
    # orientation_
    # save_npz(orientation_fp, coo_matrix(Qtensor_arr))
    logger.log("    Saving intensities to {}".format(intensities_fp))
    save_intensity_csv(intensity_arr, intensities_fp)
    # save_npz(intensities_fp, coo_matrix(snake_exists_arr))


def make_sindy_fields(
    source_images_dir,
    source_json_dir,
    save_orientations_dir,
    save_intensities_dir,
    source_jsons_depth,
    logger,
):
    source_images = find_tiffs_in_dir(source_images_dir)

    if source_jsons_depth == 0:
        json_containing_dirs = source_json_dir
    else:
        source_json_dirs_info = find_files_or_folders_at_depth(source_json_dir, source_jsons_depth - 1, folders_not_files=True)
        json_containing_dirs = [os.path.join(parent,name) for parent, name in source_json_dirs_info]

    for json_parent_dir, json_containing_dirname in source_json_dirs_info:
        json_containing_dir = os.path.join(json_parent_dir, json_containing_dirname)
        dir_relpath = os.path.relpath(json_containing_dir, source_json_dir)
        orientations_containing_dir = os.path.join(save_orientations_dir, dir_relpath)
        intensities_containing_dir = os.path.join(save_intensities_dir, dir_relpath)

        # We make sure our output directories exist to save data in
        for dirpath in [orientations_containing_dir, intensities_containing_dir]:
            if not os.path.isdir(dirpath):
                if os.path.exists(dirpath):
                    logger.FFAIL("Cannot save results in {}, path exists but is not dir".format(dirpath))
                else:
                    os.makedirs(dirpath)

        json_files = [fn for fn in os.listdir(json_containing_dir) if has_one_of_extensions(fn, [".json"])]
        json_files.sort()

        if len(json_files) != len(source_images):
            raise Exception("Number of json snake files in {} is different from number of tiffs in {} ({} vs {})".format(
                json_containing_dir,
                source_images_dir,
                len(json_files),
                len(source_images),
            ))

        for image_idx in range(len(source_images)):
            json_filename = json_files[image_idx]
            json_fp = os.path.join(json_containing_dir, json_filename)
            json_without_extension = json_filename[:-len(".json")]
            image_fp = os.path.join(source_images_dir, source_images[image_idx])
            orientation_fp = os.path.join(orientations_containing_dir, json_without_extension + "_orientations.txt")
            intensities_fp = os.path.join(intensities_containing_dir, json_without_extension + "_intensities.txt")


            make_fields(
                json_fp,
                image_fp,
                orientation_fp,
                intensities_fp,
                logger,
            )

        # make_fields(

        # )


    # source_jsons_info = find_files_or_folders_at_depth(source_json_dir, source_jsons_depth, file_extension=".json")

    # for json_containing_dirpath, json_filename in source_jsons_info:
    #     json_fp = os.path.join(json_containing_dirpath, json_filename)
    #     dir_relpath = os.path.relpath(json_containing_dirpath, source_json_dir)
    #     containing_orientation_dir = os.path.join(orientation_data_dir, dir_relpath)
    #     data_filename = json_fp[:-5] + ".npy"
    #     data_fp = os.path.join(containing_orientation_dir, data_filename)
    #     if not os.path.isdir(containing_orientation_dir):
    #         if os.path.exists(containing_orientation_dir):
    #             logger.FAIL("Cannot save orientation fields to {}, path exists but is not dir".format(data_containing_dirpath))
    #         else:
    #             os.makedirs(containing_orientation_dir)

    #     make_field_for_json(json_fp, data_fp, logger)