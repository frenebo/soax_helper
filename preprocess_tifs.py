import argparse
import argparse
import math
from snakeutils.files import readable_dir
from snakeutils.tifimage import save_3d_tif, tif_img_3d_to_arr
import os
import numpy as np
from PIL import Image
import tifffile


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Normalizes tif (useful if TIF image is too dark)')
    parser.add_argument('source_dir',type=readable_dir,help="Directory where source tif files are")
    parser.add_argument('target_dir',type=readable_dir,help="Directory to save secitoned tifs")

    args = parser.parse_args()

    source_tifs = [filename for filename in os.listdir(args.source_dir) if filename.endswith(".tif")]
    source_tifs.sort()

    if len(source_tifs) == 0:
        raise Exception("No .tif files found in {}".format(args.source_dir))

    first_tif_img = Image.open(os.path.join(args.source_dir, source_tifs[0]))
    images_are_3d = getattr(first_tif_img, "n_frames", 1) > 1

    # if just one frame
    if images_are_3d:
        first_tiff_arr = tif_img_3d_to_arr(first_tif_img)
    else:
        first_tif_arr = np.array(first_tif_img)

    min_cutoff = np.percentile(first_tif_arr,0.5)
    max_cutoff = np.percentile(first_tif_arr,99.5)

    print("Rescaling range to min val {} and max val {}".format(min_cutoff,max_cutoff))
    new_max = np.iinfo(first_tif_arr.dtype).max

    print("Data type {} with max value {}".format(first_tif_arr.dtype, new_max))

    for tif_fn in source_tifs:
        tif_fp = os.path.join(args.source_dir,tif_fn)
        preprocessed_fp = os.path.join(args.target_dir, "preprocessed_" + tif_fn)

        image_arr = np.array(Image.open(tif_fp))
        over_max_places = image_arr >= max_cutoff
        under_min_places = image_arr <= min_cutoff
        # float_arr = image_arr.astype(np.float64)
        scale_factor = float(new_max)/float((max_cutoff - min_cutoff))
        new_arr = (image_arr - min_cutoff) * scale_factor
        # new_arr = new_arr.astype(image_arr.dtype)
        new_arr[over_max_places] = new_max
        new_arr[under_min_places] = 0


        if images_are_3d:
            save_3d_tif(preprocessed_fp,new_arr)
        else:
            tifffile.imsave(preprocessed_fp,new_arr)
        print("Saved preprocessed pic as {}".format(preprocessed_fp))
