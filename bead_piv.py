import os
import trackpy as tp
import numpy as np
import pims
import math
from matplotlib import pyplot as plt

from snakeutils.logger import PrintLogger

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
    logger=PrintLogger,
    ):
    frames = pims.ImageSequenceND(source_tiff_dir, axes_identifiers=[tiff_fn_letter_before_frame_num])
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

    logger.log("Rounding up x,y bead pixel diameter to nearest odd int, {} -> {}".format(float_search_diameter_x_y, search_diameter_x_y))
    logger.log("Rounding up z bead stack diameter to nearest odd int, {} -> {}".format(float_search_diameter_z, search_diameter_z))
    diameter = (search_diameter_z, search_diameter_x_y, search_diameter_x_y)
    logger.log("Finding features with diameter {}".format(diameter))

    f = tp.batch(frames, diameter=diameter)
    f['xum'] = f['x'] * x_y_pixel_spacing_um
    f['yum'] = f['y'] * x_y_pixel_spacing_um
    f['zum'] = f['z'] * z_stack_spacing_um

    output_file = os.path.join(target_piv_data_dir, "bead_piv.json")

    linked = tp.link_df(f, linking_search_range_um, pos_columns=['xum','yum','zum'])
    # tp.plot_displacements(linked, 0, 1)

    # for search_range in [2.5, 3.0,3.5]:
    #     linked = tp.link_df(f, search_range, pos_columns=['xum', 'yum', 'zum'])
    #     hist, bins = np.histogram(np.bincount(linked.particle.astype(int)),
    #                             bins=np.arange(30), normed=True)
    #     plt.step(bins[1:], hist, label='range = {} microns'.format(search_range))
    # plt.ylabel('relative frequency')
    # plt.xlabel('track length (frames)')
    # plt.legend();
    # plt.show()
    # print(linked.particle)
    # print(type(linked.particle))
    # print(len(linked.index))
    # print(linked.shape)
    # print(linked.shape[0])
    # print(f.shape[0])
    frame_count = max(linked.frame)
    for i in range(frame_count - 1):
        before_frame = linked[linked.frame == i]
        after_frame = linked[linked.frame == i + 1]

        pos_columns = ['x', 'y', 'z']

        j = (before_frame.set_index('particle')[pos_columns].join(
            after_frame.set_index('particle')[pos_columns], rsuffix='_b'))

        for i in pos_columns:
            j['d' + i] = j[i + '_b'] - j[i]
        arrow_specs = j[pos_columns + ['d' + i for i in pos_columns]].dropna()
        print(arrow_specs)
        exit()

    # for col in linked.columns:
    #     print(col)

    # print(f)

    # raise NotImplementedError()

    # if show_things:
    #     pass
