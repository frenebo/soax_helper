import os
import numpy as np
import math
import json

def round_to_odd(num):
    return round( (num - 1)/2 ) * 2 + 1

def bead_piv(
    source_tiff_dir,
    tiff_fn_letter_before_frame_num,
    tiff_fn_letter_before_z_num,
    target_piv_data_dir,
    x_pixel_spacing_um,
    y_pixel_spacing_um,
    z_stack_spacing_um,
    bead_diameter_um,
    linking_search_range_um,

    processes,
    logger,
    ):
    import pims
    import trackpy as tp

    logger.log("Letter before frame num: {}".format(tiff_fn_letter_before_frame_num))
    frames = pims.ImageSequenceND(source_tiff_dir, axes_identifiers=[tiff_fn_letter_before_frame_num,tiff_fn_letter_before_z_num])
    logger.log("Frames:")
    logger.log(str(frames))
    logger.log("Sizes:")
    logger.log(str(frames.sizes))
    # try:
    #     logger.log("Axes:")
    #     logger.log(str(frames.axes))
    # except:
    #     logger.log("No axes")
    # Inside a frame axes are labelled x,y,c
    # frames.bundle_axes = ['c','y','x']
    frames.bundle_axes = [tiff_fn_letter_before_z_num,'y','x']
    # PIMS gives the time axis the name of identifier letter
    frames.iter_axes = [tiff_fn_letter_before_frame_num]

    float_search_diameter_x = bead_diameter_um / x_pixel_spacing_um
    float_search_diameter_y = bead_diameter_um / y_pixel_spacing_um
    float_search_diameter_z = bead_diameter_um / z_stack_spacing_um

    logger.log("Using x pixel size {x_size} um, y pixel size {y_size} um, z_spacing {z_size} um, bead size {bead_diameter_um} um".format(
        x_size = x_pixel_spacing_um,
        y_size = y_pixel_spacing_um,
        z_size = z_stack_spacing_um,
        bead_diameter_um = bead_diameter_um,
        ))
    logger.log("In x dimension we expect beads to be {} pixels large".format(float_search_diameter_x))
    logger.log("In y dimension we expect beads to be {} pixels large".format(float_search_diameter_y))
    logger.log("In z dimension we expect beads to be {} stacks large".format(float_search_diameter_z))

    search_diameter_x = round_to_odd(float_search_diameter_x)
    search_diameter_y = round_to_odd(float_search_diameter_y)
    search_diameter_z = round_to_odd(float_search_diameter_z)

    if search_diameter_x < 1:
        search_diameter_x = 1
    if search_diameter_y < 1:
        search_diameter_y = 1
    if search_diameter_z < 1:
        search_diameter_z = 1

    logger.log("Rounding up x bead pixel diameter to nearest odd int, {} -> {}".format(float_search_diameter_x, search_diameter_x))
    logger.log("Rounding up y bead pixel diameter to nearest odd int, {} -> {}".format(float_search_diameter_y, search_diameter_y))
    logger.log("Rounding up z bead stack diameter to nearest odd int, {} -> {}".format(float_search_diameter_z, search_diameter_z))
    diameter = (search_diameter_z, search_diameter_x, search_diameter_y)
    logger.log("Finding features with diameter {}".format(diameter))
    logger.log("After finding features, cross-time-frame linking will be done with linking search range {} um".format(linking_search_range_um))

    f = tp.batch(frames, diameter=diameter, processes=processes)
    f['xum'] = f['x'] * x_pixel_spacing_um
    f['yum'] = f['y'] * y_pixel_spacing_um
    f['zum'] = f['z'] * z_stack_spacing_um

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
    logger.log("XYZ um min and max:")
    logger.log("min {} {} {}, max {} {} {}".format(
        str(f.xum.min()),
        str(f.yum.min()),
        str(f.zum.min()),
        str(f.xum.max()),
        str(f.yum.max()),
        str(f.zum.max()),
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

    # Linking is faster if using a predictor for where the particles will go
    # pred = tp.predict.NearestVelocityPredict()
    pred = tp
    linked = pred.link_df(f, linking_search_range_um,  pos_columns=['xum','yum','zum'])

    # frame_count = max(linked.frame)
    linked.to_csv("linked_df.csv")

    # data_filename_template = "motion_start_frame{{idx:0{str_length}.0f}}.json".format(str_length=len(str(frame_count - 1)))
    # data_filename_template = "motion_start_frame{{idx:0{str_length}.0f}}.csv".format(str_length=len(str(frame_count - 1)))
    # for i in range(frame_count):
    #     frame = linked[linked.frame == i]
    #     frame.to_csv(data_filename_template.format(idx=i))
        # before_frame = linked[linked.frame == i]

        # after_frame = linked[linked.frame == i + 1]
        # before_frame.

        # pos_columns = ['x', 'y', 'z']

        # j = (before_frame.set_index('particle')[pos_columns].join(
        #     after_frame.set_index('particle')[pos_columns], rsuffix='_b'))

        # for col_i in pos_columns:
        #     j['d' + col_i] = j[col_i + '_b'] - j[col_i]

        # bead_movement_info = j[pos_columns + ['d' + i for i in pos_columns]].dropna()
        # # print(arrow_specs)
        # bead_motions = bead_movement_info.to_dict(orient='index')

        # motions_save_path = os.path.join(target_piv_data_dir, data_filename_template.format(idx=i))

        # with open(motions_save_path, "w") as f:
        #     json.dump(bead_motions, f)
