import argparse
import argparse
import math
from snakeutils.files import readable_dir
from snakeutils.tifimage import save_3d_tif, tif_img_3d_to_arr
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

    first_tif_img = Image.open(os.path.join(source_dir, source_tifs[0]))
    images_are_3d = getattr(first_tif_img, "n_frames", 1) > 1

    # if just one frame
    if images_are_3d:
        logger.log("Opening and saving images as 3D")
        first_tiff_arr = tif_img_3d_to_arr(first_tif_img)
    else:
        first_tif_arr = np.array(first_tif_img)

    max_cutoff = np.percentile(first_tif_arr,max_cutoff_percent)
    min_cutoff = np.percentile(first_tif_arr,min_cutoff_percent)

    logger.log("Rescaling range to max val {}".format(max_cutoff))
    new_max = np.iinfo(first_tif_arr.dtype).max
    scale_factor = float(new_max)/float(max_cutoff - min_cutoff)

    logger.log("Data type {} with max value {}".format(first_tif_arr.dtype, new_max))

    for tif_fn in source_tifs:
        tif_fp = os.path.join(source_dir,tif_fn)
        preprocessed_fp = os.path.join(target_dir, "preprocessed_" + tif_fn)

        image_arr = np.array(Image.open(tif_fp))
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
