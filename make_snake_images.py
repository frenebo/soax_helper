import sys
import os
from matplotlib import pyplot as plt
import numpy as np
from snakeutils.files import extract_snakes, readable_dir, find_files_or_folders_at_depth, has_one_of_extensions
import argparse
from PIL import Image
from snakeutils.logger import PrintLogger, Colors
import json

def infer_height_width(filename):
    # Expecting "sec_{height_lower}-{height_upper}_{width_lower}-{width_upper}_{depth_lower}-{depth_upper}.tif"
    if not (filename.startswith("sec_") and has_one_of_extensions(filename, [".tif", ".tiff"])):
        return None,None

    try:
        if has_one_of_extensions(filename, [".tif"]):
            info_fn_part = filename[4:-4]
        elif has_one_of_extensions(filename, [".tiff"]):
            info_fn_part = filename[4:-5]
        else:
            raise Exception("case not accounted for")
        height_range,width_range,depth_range = info_fn_part.split("_")

        height_lower,height_upper = height_range.split("-")
        width_lower,width_upper = width_range.split("-")
        depth_lower,depth_upper = depth_range.split("-")

        height = height_upper - height_lower
        width = width_upper - width_lower

        return height,width
    except:
        return None,None

def save_images_for_dir_snakes(dir_name,image_dir_name,colorful,logger,image_width=None,image_height=None,background_img_dir=None):
    snake_filenames = [filename for filename in os.listdir(dir_name) if has_one_of_extensions(filename, [".json"])]
    snake_filenames.sort()

    if background_img_dir is not None:
        background_image_filenames = [filename for filename in os.listdir(background_img_dir) if has_one_of_extensions(filename, [".jpg", ".jpeg", ".tif", ".tiff"])]
        background_image_filenames.sort()
        logger.log("Found background images: ")
        logger.log(", ".join(background_image_filenames))

    for img_idx, snake_filename in enumerate(snake_filenames):
        snakes_json_fp = os.path.join(dir_name,snake_filename)
        logger.log("Showing snakes for {}".format(snakes_json_fp))

        if background_img_dir is not None and img_idx < len(background_image_filenames):
            background_img_fp = os.path.join(background_img_dir,background_image_filenames[img_idx])
            logger.log("  Using background image {}".format(background_img_fp))
            background_img = Image.open(background_img_fp).convert('RGB')
            plt.imshow(background_img)
        else:
            background_img = None

        if image_width is None or image_height is None:
            if background_img is not None:
                image_width, image_height = background_img.size
            else:
                logger.error("Must provide width and height of images")
        with open(snakes_json_fp, "r") as f:
            snakes = json.load(f)

        for snake_idx, snake_pts in enumerate(snakes):
            snake_positions = [snake_part["pos"] for snake_part in snake_pts]
            snake_positions = np.array(snake_positions)

            x,y = snake_positions.T[:2]

            if colorful:
                plt.plot(x,y)
            else:
                if background_img is None:
                    plt.plot(x,y,'b')
                else:
                    plt.plot(x,y,'y')

        # some_snakefile.tif => some_snakefile.jpg
        save_img_filename = "".join(snake_filename.split(".")[:-1]) + ".png"
        save_img_fp = os.path.join(image_dir_name,save_img_filename)

        plt.axes().set_aspect('equal', adjustable='box')
        # invert y axis
        plt.axis([0,image_width,image_height,0])
        plt.xlabel("x")
        plt.ylabel("y")
        plt.savefig(save_img_fp)
        logger.success("  Saved image to {}".format(save_img_fp))
        # clear figure so we can do the next plot
        plt.clf()

def make_snake_images(
    dir_name,
    image_dir,
    width,
    height,
    snake_files_depth,
    colorful,
    background_img_dir,
    logger=PrintLogger,
    ):
    if snake_files_depth == 0:
        snake_dirs = [dir_name]
        image_dirs = [image_dir]
    else:
        snake_dirs = []
        image_dirs = []
        snake_dirs_depth = snake_files_depth - 1
        snake_folder_info = find_files_or_folders_at_depth(dir_name, snake_dirs_depth, folders_not_files=True)

        for parent_dir, snake_dir_name in snake_folder_info:
            snake_dir_path = os.path.join(parent_dir, snake_dir_name)
            snake_folder_relative_path = os.path.relpath(snake_dir_path, dir_name)
            image_dir_path = os.path.join(image_dir, snake_folder_relative_path)

            if not os.path.isdir(image_dir_path):
                if os.path.exists(image_dir_path):
                    logger.error("Cannot save images in {}, this path exists but is not dir".format(image_dir_path))
                    continue
                else:
                    os.makedirs(image_dir_path)

            snake_dirs.append(snake_dir_path)
            image_dirs.append(image_dir_path)

    logger.log("Making images from snake files in :{}".format(", ".join(snake_dirs)))
    print("Snake dirs: ")
    print(snake_dirs)
    print("Image dirs: ")
    print(image_dirs)

    for i in range(len(snake_dirs)):
        logger.log("Making snakes for {}, saving in {}".format(snake_dirs[i],image_dirs[i]))
        save_images_for_dir_snakes(
            snake_dirs[i],
            image_dirs[i],
            colorful,
            logger,
            width,
            height,
            background_img_dir,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('snake_dir',type=readable_dir,help="Source directory where snake text files are")
    parser.add_argument('image_dir',type=readable_dir,help="Target directory to save graphed snakes")
    parser.add_argument('--width',default=None,type=int,help="Width dimension of frame. Optional if can guess from image names")
    parser.add_argument('--height',default=None,type=int,help="Width dimension of frame. Optional if can guess from image names")
    parser.add_argument('--snake_files_depth',default=0,type=int,help="Subdir depth at which to find snake images in snake_dir")
    parser.add_argument('-c','--colorful', action='store_true',help="Use different colors for each snake")
    parser.add_argument('--background_img_dir', default=None,type=readable_dir,help="Directory with images to use as backgrounds for TIFs")

    args = parser.parse_args()

    make_snake_images(
        args.snake_dir,
        args.image_dir,
        args.width,
        args.height,
        args.snake_files_depth,
        args.colorful,
        args.background_img_dir,
    )
