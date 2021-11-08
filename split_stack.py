import argparse
from snakeutils.tifimage import pil_img_3d_to_np_arr, save_3d_tif
import os
from PIL import Image

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Split 3D Tiff into its 2D frames')
    parser.add_argument('source_tiff_path')
    parser.add_argument('target_directory')

    args = parser.parse_args()

    if not os.path.exists(args.target_directory):
        os.makedirs(args.target_directory)
    else:
        if not os.path.isdir(args.target_directory):
            raise Exception("Bad target directory '{}': should be a directory to put the tif frames into".format(args.target_directory))

    pil_img = Image.open(args.source_tiff_path)
    np_arr = pil_img_3d_to_np_arr(pil_img)

    tiff_name = os.path.split(args.source_tiff_path)[-1]

    stack_num = np_arr.shape[2]
    for i in range(stack_num):
        fp = os.path.join(args.target_directory, "{}_".format(i) + tiff_name)
        save_3d_tif(fp, save_3d_np_arr[i])
        print("Saved {}".format(fp))