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

    print("shape: {}".format(np_arr.shape))

    tiff_name = os.path.split(args.source_tiff_path)[-1]

    stack_num = np_arr.shape[2]
    # "_{filename_tag}{{{name}:0{str_length}.{decimals}f}}"
    prefix_template = "{{idx:0{str_length}.0f}}_".format(str_length=len(str(stack_num)))
    for i in range(stack_num):
        fp = os.path.join(args.target_directory, prefix_template.format(idx=i) + tiff_name)
        save_3d_tif(fp, np_arr[:,:,i:i+1])
        print("Saved {}".format(fp))