import argparse
import os
from PIL import Image

from .snakeutils.files import  find_tiffs_in_dir
from .snakeutils.tifimage import open_tiff_as_np_arr, save_3d_tif

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Split 3D Tiffs into it 2D frames')
    parser.add_argument('source_tiff_dir')
    parser.add_argument('target_directory')

    args = parser.parse_args()

    split_stacks(args.source_tiff_dir, args.target_directory)

def split_stacks(source_tiff_dir, target_directory):

    if not os.path.isdir(source_tiff_dir):
        raise Exception("Bad source directory '{}': should be a directory with TIFF frames inside".format(args.source_tiff_dir))


    if not os.path.exists(target_directory):
        os.makedirs(args.target_directory)
    else:
        if not os.path.isdir(target_directory):
            raise Exception("Bad target directory '{}': should be a directory to put the TIFF frames into".format(args.target_directory))

    source_tiffs = find_tiffs_in_dir(source_tiff_dir)
    for tiff_fn in source_tiffs:
        tiff_path = os.path.join(source_tiff_dir, tiff_fn)

        # tiff_path =
        np_arr = open_tiff_as_np_arr(tiff_path)

        print("shape: {}".format(np_arr.shape))

        # tiff_name = os.path.split(tiff_path)[-1]
        tiff_name = os.path.splitext(tiff_fn)[0]

        stack_num = np_arr.shape[2]
        # "_{filename_tag}{{{name}:0{str_length}.{decimals}f}}"
        prefix_template = "_z{{idx:0{str_length}.0f}}".format(str_length=len(str(stack_num - 1)))
        for i in range(stack_num):
            slice_tiff_fn = tiff_name + suffix_template.format(idx=i) + ".tif"
            slice_fp = os.path.join(target_directory, slice_tiff_fn)

            # fp = os.path.join(target_directory, prefix_template.format(idx=i) + tiff_name)
            save_3d_tif(slice_fp, np_arr[:,:,i:i+1])
            print("Saved {}".format(slice_fp))