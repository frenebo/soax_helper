import os
import trackpy as tp
import pims
import math

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
    logger=PrintLogger,
    show_things=False,
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

    print(f)

    raise NotImplementedError()

    # if show_things:
    #     pass
