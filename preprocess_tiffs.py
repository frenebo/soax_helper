import argparse
import argparse
import math
from snakeutils.files import readable_dir, pil_img_3d_to_np_arr
from snakeutils.tifimage import save_3d_tif, tiff_img_3d_to_arr
import os
import numpy as np
from PIL import Image
import tifffile
from snakeutils.logger import PrintLogger

def preprocess_tiffs(source_dir,target_dir,max_cutoff_percent,min_cutoff_percent,logger=PrintLogger):
    source_tifs = [filename for filename in os.listdir(source_dir) if filename.endswith(".tif")]
    source_tifs.sort()

    if len(source_tifs) == 0:
        logger.error("No .tif files found in {}".format(source_dir))
        return

    first_tiff_img = Image.open(os.path.join(source_dir, source_tifs[0]))
    images_are_3d = getattr(first_tiff_img, "n_frames", 1) > 1

    # if just one frame
    if images_are_3d:
        logger.log("Opening and saving images as 3D")
        first_tiff_arr = tiff_img_3d_to_arr(first_tiff_img)
    else:
        first_tiff_arr = np.array(first_tiff_img)

    max_cutoff = np.percentile(first_tiff_arr,max_cutoff_percent)
    min_cutoff = np.percentile(first_tiff_arr,min_cutoff_percent)

    logger.log("Rescaling range to max val {}".format(max_cutoff))
    new_max = np.iinfo(first_tiff_arr.dtype).max
    scale_factor = float(new_max)/float(max_cutoff - min_cutoff)

    logger.log("Data type {} with max value {}".format(first_tiff_arr.dtype, new_max))

    for tiff_fn in source_tifs:
        tiff_fp = os.path.join(source_dir,tiff_fn)
        preprocessed_fp = os.path.join(target_dir, "preprocessed_" + tiff_fn)

        pil_img = Image.open(tiff_fp)
        # If 2D
        if getattr(pil_img, "n_frames", 1) == 1:
            image_arr = np.array(pil_img)
        # if 3D
        else:
            image_arr = pil_img_3d_to_np_arr(pil_img)

        over_max_places = image_arr >= max_cutoff
        under_min_places = image_arr <= min_cutoff

        # float_arr = image_arr.astype(np.float64)
        new_arr = (image_arr - min_cutoff)* scale_factor

        new_arr = new_arr.astype(image_arr.dtype)
        new_arr[over_max_places] = new_max
        new_arr[under_min_places] = 0

        logger.log("New min:  {}".format(new_arr.min()))
        logger.log("New max: {}".format(new_arr.max()))

        if images_are_3d:
            save_3d_tif(preprocessed_fp,new_arr)
        else:
            tifffile.imsave(preprocessed_fp,new_arr)
        logger.log("Saved preprocessed pic as {}".format(preprocessed_fp))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Normalizes tif (useful if TIF image is too dark)')
    parser.add_argument('source_dir',type=readable_dir,help="Directory where source tif files are")
    parser.add_argument('target_dir',type=readable_dir,help="Directory to save secitoned tifs")
    max_default_percentile = 95.5
    parser.add_argument('--max_cutoff_percent',type=float,default=max_default_percentile,help="Pixel brightness percentile to set image max to. Default {}".format(max_default_percentile))
    min_default_percentile = 0.1
    parser.add_argument('--min_cutoff_percent',type=float,default=min_default_percentile,help="Pixel brightness percentile to set image min to. Default {}".format(min_default_percentile))

    args = parser.parse_args()

    preprocess_tiffs(
        args.source_dir,
        args.target_dir,
        args.max_cutoff_percent,
        args.min_cutoff_percent,
    )
