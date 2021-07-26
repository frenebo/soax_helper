import argparse
import math
from snakeutils.files import readable_dir
from snakeutils.tifimage import save_3d_tif, tif_img_3d_to_arr
import os
import numpy as np
from PIL import Image

def section_tif(tif_filepath,sectioned_dir,section_max_size):
    print("Processing {}".format(tif_filepath))

    pil_img = Image.open(tif_filepath)

    tif_is_3d = getattr(pil_img, "n_frames", 1) != 1

    width = pil_img.width
    height = pil_img.height
    if tif_is_3d:
        depth = pil_img.n_frames
        img_arr = tif_img_3d_to_arr(pil_img)
    else:
        img_arr = np.array(pil_img)

    # Ceil because we want to have slices on the smaller size if width/height/depth is not
    # exactly divisible by section_size
    height_slices = math.ceil(height / section_max_size)
    width_slices = math.ceil(width / section_max_size)
    if tif_is_3d:
        depth_slices = math.ceil(depth / section_max_size)

    section_height = math.floor(height / height_slices)
    section_width = math.floor(width / width_slices)
    if tif_is_3d:
        section_depth = math.floor(depth / depth_slices)

    height_boundaries = [i*section_height for i in range(height_slices)] + [height]
    width_boundaries = [i*section_width for i in range(width_slices)] + [width]
    if tif_is_3d:
        depth_boundaries = [i*section_depth for i in range(depth_slices)] + [depth]

    if tif_is_3d:
        for width_idx in range(width_slices):
            for height_idx in range(height_slices):
                for depth_idx in range(depth_slices):
                    height_lower = height_boundaries[height_idx]
                    height_upper = height_boundaries[height_idx + 1]
                    width_lower = width_boundaries[width_idx]
                    width_upper = width_boundaries[width_idx + 1]
                    depth_lower = depth_boundaries[depth_idx]
                    depth_upper = depth_boundaries[depth_idx + 1]
                    section_arr = img_arr[
                        height_lower:height_upper,
                        width_lower:width_upper,
                        depth_lower:depth_upper,
                    ]
                    section_filename = "3Dsec_{height_lower}-{height_upper}_{width_lower}-{width_upper}_{depth_lower}-{depth_upper}.tif".format(
                        height_lower=height_lower,
                        height_upper=height_upper,
                        width_lower=width_lower,
                        width_upper=width_upper,
                        depth_lower=depth_lower,
                        depth_upper=depth_upper,
                    )
                    section_filepath = os.path.join(sectioned_dir,section_filename)

                    save_3d_tif(section_filepath,section_arr)
    else:
        for width_idx in range(width_slices):
            for height_idx in range(height_slices):
                    height_lower = height_boundaries[height_idx]
                    height_upper = height_boundaries[height_idx + 1]
                    width_lower = width_boundaries[width_idx]
                    width_upper = width_boundaries[width_idx + 1]

                    section_arr = img_arr[
                        height_lower:height_upper,
                        width_lower:width_upper,
                    ]

                    section_filename = "2Dsec_{height_lower}-{height_upper}_{width_lower}-{width_upper}.tif".format(
                        height_lower=height_lower,
                        height_upper=height_upper,
                        width_lower=width_lower,
                        width_upper=width_upper,
                    )
                    section_filepath = os.path.join(sectioned_dir,section_filename)

                    tifffile.imsave(section_filepath,section_arr)

    if tif_is_3d:
        section_num = width_slices*height_slices*depth_slices
    else:
        section_num = width_slices*height_slices

    print("  Split {} into {} sections in {}".format(
        tif_filepath,
        section_num,
        sectioned_dir))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('section_max_size',type=int,help="Maximum width/height/depth of a sextion (pixels along)")
    parser.add_argument('source_dir',type=readable_dir,help="Directory where source tif files are")
    parser.add_argument('target_dir',type=readable_dir,help="Directory to save secitoned tifs")

    args = parser.parse_args()

    if args.section_max_size <= 0:
        raise Exception("Section max size must be positive. Invalid value {}".format(args.section_size))

    source_tifs = [filename for filename in os.listdir(args.source_dir) if filename.endswith(".tif")]
    source_tifs.sort()

    for tif_fn in source_tifs:
        tif_fp = os.path.join(args.source_dir,tif_fn)

        # remove .tif from file name
        image_name_extensionless = tif_fn[:-4]

        sectioned_dir = os.path.join(args.target_dir, "sectioned_" + image_name_extensionless)

        if os.path.exists(sectioned_dir):
            raise Exception("Directory {} already exists".format(sectioned_dir))

        os.mkdir(sectioned_dir)

        section_tif(tif_fp,sectioned_dir,args.section_max_size)
