import os
import numpy as np
import math
import json


def up_to_nearest_odd(num):
    return math.ceil((num - 1)/2)*2 + 1

def bead_piv(
    source_tiff_dir,
    tiff_fn_letter_before_frame_num,
    tiff_fn_letter_before_z_num,
    target_piv_data_dir,
    brightness_threshold,
    noise_size_xyz,
    bead_pixel_searchsize_xyz,
    percentile,
    processes,

    logger,
    ):
    import pims
    import trackpy as tp

    for beadpixdim in bead_pixel_searchsize_xyz:
        if beadpixdim < 0:
            raise Exception("Bead pixel dimensions cannot be negative: ", str(bead_pixel_searchsize_xyz))

    x_noise_size, y_noise_size, z_noise_size = noise_size_xyz

    logger.log("Letter before frame num: {}".format(tiff_fn_letter_before_frame_num))
    frames = pims.ImageSequenceND(source_tiff_dir, axes_identifiers=[tiff_fn_letter_before_frame_num,tiff_fn_letter_before_z_num])
    logger.log("Frames:")
    logger.log(str(frames))
    logger.log("Sizes:")
    logger.log(str(frames.sizes))

    frames.bundle_axes = [tiff_fn_letter_before_z_num,'y','x']
    # PIMS gives the time axis the name of identifier letter
    frames.iter_axes = [tiff_fn_letter_before_frame_num]

    logger.log("Using noise size in x,y,z: {},{},{}".format(x_noise_size, y_noise_size, z_noise_size))

    search_size_xyz = [up_to_nearest_odd(size) for size in bead_pixel_searchsize_xyz]

    search_diameter_x, search_diameter_y, search_diameter_z = search_size_xyz

    logger.log("In x dimension we search for beads {} pixels large".format(search_diameter_x))
    logger.log("In y dimension we search for beads {} pixels large".format(search_diameter_y))
    logger.log("In z dimension we search for beads {} stacks large".format(search_diameter_z))

    diameter = (search_diameter_z, search_diameter_x, search_diameter_y)
    logger.log("Finding features with diameter {}".format(diameter))


    noise_size_zxy = (z_noise_size, x_noise_size, y_noise_size)
    f = tp.batch(frames, percentile=percentile, diameter=diameter, processes=processes, threshold=brightness_threshold, noise_size=noise_size_zxy)

    logger.log("Columns:")
    for col in f.columns:
        logger.log("   " + str(col))
    logger.log("Shape: ")
    logger.log(str(f.shape))
    logger.log("Size: ")
    logger.log(str(f.size))
    logger.log("Unique frames: ")
    logger.log(str(f.frame.unique()))
    logger.log("XYZ min and max:")
    logger.log("min {} {} {}, max {} {} {}".format(
        str(f.x.min()),
        str(f.y.min()),
        str(f.z.min()),
        str(f.x.max()),
        str(f.y.max()),
        str(f.z.max()),
    ))
    logger.log("size min and max:")
    logger.log("min {} {} {}, max {} {} {}".format(
        str(f.size_x.min()),
        str(f.size_y.min()),
        str(f.size_z.min()),
        str(f.size_x.max()),
        str(f.size_y.max()),
        str(f.size_z.max()),
    ))

    f.to_csv(os.path.join(target_piv_data_dir, "unlinked_beads.csv"))
    logger.log("Saved to csv file")

