import argparse
import os
from PIL import Image

from .snakeutils.tifimage import open_tiff_as_np_arr, save_3d_tif

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Split 3D Tiff into its 2D frames')
    parser.add_argument('source_tiff_path')
    parser.add_argument('target_directory')

    args = parser.parse_args()

    if not os.path.exists(args.target_directory):
        os.makedirs(args.target_directory)
    else:
        if not os.path.isdir(args.target_directory):
            raise Exception("Bad target directory '{}': should be a directory to put the TIFF frames into".format(args.target_directory))

    np_arr = open_tiff_as_np_arr(args.source_tiff_path)

    print("shape: {}".format(np_arr.shape))

    tiff_name = os.path.split(args.source_tiff_path)[-1]

    stack_num = np_arr.shape[2]
    # "_{filename_tag}{{{name}:0{str_length}.{decimals}f}}"
    prefix_template = "{{idx:0{str_length}.0f}}_".format(str_length=len(str(stack_num - 1)))
    for i in range(stack_num):
        fp = os.path.join(args.target_directory, prefix_template.format(idx=i) + tiff_name)
        save_3d_tif(fp, np_arr[:,:,i:i+1])
        print("Saved {}".format(fp))