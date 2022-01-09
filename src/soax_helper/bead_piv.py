import os
import numpy as np
import math
import json


def round_to_odd(num):
    return round( (num - 1)/2 ) * 2 + 1

def bead_piv(
    source_tiff_dir,
    tiff_fn_letter_before_frame_num,
    target_piv_data_dir,
    x_y_pixel_spacing_um,
    z_stack_spacing_um,
    bead_diameter_um,
    linking_search_range_um,
    processes,
    logger,
    ):
    import pims
    import trackpy as tp

    logger.log("Letter before frame num: {}".format(tiff_fn_letter_before_frame_num))
    frames = pims.ImageSequenceND(source_tiff_dir, axes_identifiers=[tiff_fn_letter_before_frame_num])
    logger.log("Frames")
    logger.log(str(frames))
    try:
        logger.log("Axes:")
        logger.log(str(frames.axes))
    except:
        logger.log("No axes")
    # Inside a frame axes are labelled x,y,c
    frames.bundle_axes = ['c','y','x']
    # PIMS gives the time axis the name of identifier letter
    frames.iter_axes = [tiff_fn_letter_before_frame_num]

    float_search_diameter_x_y = bead_diameter_um / x_y_pixel_spacing_um
    float_search_diameter_z = bead_diameter_um / z_stack_spacing_um

    logger.log("Using x_y_pixel size {x_y_size} um, z_spacing {z_size} um, bead size {bead_diameter_um} um".format(
        x_y_size = x_y_pixel_spacing_um,
        z_size = z_stack_spacing_um,
        bead_diameter_um = bead_diameter_um,
        ))
    logger.log("In x y dimension we expect beads to be {} pixels large".format(float_search_diameter_x_y))
    logger.log("In z dimension we expect beads to be {} stacks large".format(float_search_diameter_z))

    search_diameter_x_y = round_to_odd(float_search_diameter_x_y)
    search_diameter_z = round_to_odd(float_search_diameter_z)

    if search_diameter_x_y < 1:
        search_diameter_x_y = 1
    if search_diameter_z < 1:
        search_diameter_z = 1

    logger.log("Rounding up x,y bead pixel diameter to nearest odd int, {} -> {}".format(float_search_diameter_x_y, search_diameter_x_y))
    logger.log("Rounding up z bead stack diameter to nearest odd int, {} -> {}".format(float_search_diameter_z, search_diameter_z))
    diameter = (search_diameter_z, search_diameter_x_y, search_diameter_x_y)
    logger.log("Finding features with diameter {}".format(diameter))

    f = tp.batch(frames, diameter=diameter, processes=processes)
    f['xum'] = f['x'] * x_y_pixel_spacing_um
    f['yum'] = f['y'] * x_y_pixel_spacing_um
    f['zum'] = f['z'] * z_stack_spacing_um

    output_file = os.path.join(target_piv_data_dir, "bead_piv.json")

    linked = tp.link_df(f, linking_search_range_um, pos_columns=['xum','yum','zum'])

    frame_count = max(linked.frame)

    data_filename_template = "motion_start_frame{{idx:0{str_length}.0f}}.json".format(str_length=len(str(frame_count - 1)))
    for i in range(frame_count - 1):
        before_frame = linked[linked.frame == i]
        after_frame = linked[linked.frame == i + 1]

        pos_columns = ['x', 'y', 'z']

        j = (before_frame.set_index('particle')[pos_columns].join(
            after_frame.set_index('particle')[pos_columns], rsuffix='_b'))

        for col_i in pos_columns:
            j['d' + col_i] = j[col_i + '_b'] - j[col_i]

        bead_movement_info = j[pos_columns + ['d' + i for i in pos_columns]].dropna()
        # print(arrow_specs)
        bead_motions = bead_movement_info.to_dict(orient='index')

        motions_save_path = os.path.join(target_piv_data_dir, data_filename_template.format(idx=i))

        with open(motions_save_path, "w") as f:
            json.dump(bead_motions, f)
