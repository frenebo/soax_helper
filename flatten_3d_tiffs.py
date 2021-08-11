from snakeutils.files import has_one_of_extensions, pil_img_3d_to_np_arr
# import argparse
from PIL import Image
import numpy as np
import tifffile
import os
from snakeutils.logger import PrintLogger, Colors

def flatten_3d_pil_img_return_arr(pil_img, logger):
    arr_3d = pil_img_3d_to_np_arr(pil_img)
    # Maximum intensity projection
    arr_2d = np.max(arr_3d,axis=2)

    return arr_2d


def flatten_3d_tiffs(source_dir,target_dir,logger=PrintLogger):

    tiff_names = [name for name in os.listdir(source_dir) if has_one_of_extensions(name, [".tif", ".tiff"])]
    tiff_names.sort()

    for src_tiff_fn in tiff_names:
        fp = os.path.join(source_dir,src_tiff_fn)
        logger.log("Processing {}".format(fp))
        pil_img = Image.open(fp)

        # if just one frame
        if getattr(pil_img, "n_frames", 1) == 1:
            logger.error("Cannot flatten, TIF {} is already 2D".format(fp))
            return

        arr_2d = flatten_3d_pil_img_return_arr(pil_img, logger)

        new_tiff_fn = "2d_" + src_tiff_fn
        new_fp = os.path.join(target_dir, new_tiff_fn)
        logger.success("  Saving flattened tif as {}".format(new_fp))

        tifffile.imsave(new_fp,arr_2d)
