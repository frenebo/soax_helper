import os


def link_beads(
    pixel_spacing_um_xyz,
    linking_search_range_um,
    source_piv_data_dir,
    target_linked_bead_data_dir,
    logger,
    ):
    import pims
    import trackpy as tp
    import pandas as pd

    unlinked_fp = os.path.join(source_piv_data_dir, "unlinked_beads.csv")

    if not os.path.exists(unlinked_fp):
        logger.FAIL("Cannot find unlinked beads file at {}".format(unlinked_fp))

    f = pd.read_csv(unlinked_fp)


    x_pixel_spacing_um, y_pixel_spacing_um, z_stack_spacing_um = pixel_spacing_um_xyz

    logger.log("Using x pixel size {x_size} um, y pixel size {y_size} um, z_spacing {z_size} um".format(
        x_size = x_pixel_spacing_um,
        y_size = y_pixel_spacing_um,
        z_size = z_stack_spacing_um,
    ))


    f['xum'] = f['x'] * x_pixel_spacing_um
    f['yum'] = f['y'] * y_pixel_spacing_um
    f['zum'] = f['z'] * z_stack_spacing_um

    # Linking is faster if using a predictor for where the particles will go
    # pred = tp.predict.NearestVelocityPredict()
    pred = tp
    logger.log("After finding features, cross-time-frame linking will be done with linking search range {} um".format(linking_search_range_um))
    linked = pred.link_df(f, linking_search_range_um,  pos_columns=['xum','yum','zum'])

    linked.to_csv(os.path.join(target_linked_bead_data_dir, "linked_df.csv"))