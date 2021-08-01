import sys
import os
from matplotlib import pyplot as plt
import numpy as np
from snakeutils.files import extract_snakes, readable_dir
import argparse
from PIL import Image
from snakeutils.logger import PrintLogger, Colors

def infer_height_width(filename):
    # Expecting "sec_{height_lower}-{height_upper}_{width_lower}-{width_upper}_{depth_lower}-{depth_upper}.tif"
    if not (filename.startswith("sec_") and filename.endswith(".tif")):
        return None,None

    try:
        height_range,width_range,depth_range = filename[4:-4].split("_")

        height_lower,height_upper = height_range.split("-")
        width_lower,width_upper = width_range.split("-")
        depth_lower,depth_upper = depth_range.split("-")

        height = height_upper - height_lower
        width = width_upper - width_lower

        return height,width
    except:
        return None,None

def save_images_for_dir_snakes(dir_name,image_dir_name,colorful,logger,image_width=None,image_height=None,background_img_dir=None):
    snake_filenames = [filename for filename in os.listdir(dir_name) if (filename.endswith(".txt") or ffilename.endswith(".pickle"))]
    snake_filenames.sort()

    if background_img_dir is not None:
        background_image_filenames = [filename for filename in os.listdir(background_img_dir) if (filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".tif"))]
        background_image_filenames.sort()
        logger.log("Found background images: ")
        logger.log(", ".join(background_image_filenames))

    for img_idx, snake_filename in enumerate(snake_filenames):
        fp = os.path.join(dir_name,snake_filename)
        logger.log("Showing snakes for {}".format(fp))

        if background_img_dir is not None and img_idx < len(background_image_filenames):
            background_img_fp = os.path.join(background_img_dir,background_image_filenames[img_idx])
            logger.log("  Using background image {}".format(background_img_fp))
            background_img = Image.open(background_img_fp)
            plt.imshow(background_img)
        else:
            background_img = None

        if image_width is None or image_height is None:
            if background_img is not None:
                image_width, image_height = background_img.size
            else:
                image_height,image_width = infer_height_width(snake_filename)
                if image_width is None:
                    logger.error("Must provide width and height of images, could not determine from filename {}".format(snake_filename))
                    return
        if fp.endswith(".txt"):
            with open(fp, "r") as snake_file:
                try:
                    snakes = extract_snakes(snake_file)
                except Exception as e:
                    logger.FAIL(repr(e))
        elif fp.endswith(".pickle"):
            with open(fp, "r") as snake_file:
                snakes = pickle.load(snake_file)
        else:
            logger.error("Unsupported extension with file {}".format(fp))
            return

        for snake_idx, snake_pts in enumerate(snakes):
            snake_pts = np.array(snake_pts)

            x,y = snake_pts.T[:2]

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
    use_subdirs,
    use_subsubdirs,
    colorful,
    background_img_dir,
    logger=PrintLogger,
    ):
    if (background_img_dir is not None) and use_subsubdirs:
        logger.FAIL("Background images not supported with depth > 1")

    snake_dirs = []
    image_dirs = []

    if use_subsubdirs:
        subs = [name for name in os.listdir(dir_name) if os.path.isdir(os.path.join(dir_name,name))]
        for sub in subs:
            subsubs = [name for name in os.listdir(os.path.join(dir_name,sub)) if os.path.isdir(os.path.join(dir_name,sub,name))]
            image_subdir_path = os.path.join(image_dir,sub)
            os.mkdir(image_subdir_path)
            for subsub in subs:
                snake_subsubdir_path = os.path.join(dir_name,sub,subsub)
                image_subsubdir_path = os.path.join(image_dir,sub,subsub)
                os.mkdir(image_subsubdir_path)
                snake_dirs.append(snake_subsubdir_path)
                image_dirs.append(image_subsubdir_path)
    elif use_subdirs:
        subs = [name for name in os.listdir(dir_name) if os.path.isdir(os.path.join(dir_name,name))]
        for sub in subs:
            snake_subdir_path = os.path.join(dir_name,sub)
            image_subdir_path = os.path.join(image_dir,sub)
            os.mkdir(image_subdir_path)
            snake_dirs.append(snake_subdir_path)
            image_dirs.append(image_subdir_path)
    else:
        snake_dirs.append(dir_name)
        image_dirs.append(image_dir)

    snake_dirs.sort()
    logger.log("Making images from snake files in {}".format(", ".join(snake_dirs)))

    for i in range(len(snake_dirs)):
        logger.log("Making snakes for {}, saving in {}".format(snake_dirs[i],image_dirs[i]))
        save_images_for_dir_snakes(
            snake_dirs[i],
            image_dirs[i],
            colorful,
            width,
            height,
            background_img_dir,
            logger,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('snake_dir',type=readable_dir,help="Source directory where snake text files are")
    parser.add_argument('image_dir',type=readable_dir,help="Target directory to save graphed snakes")
    parser.add_argument('--width',default=None,type=int,help="Width dimension of frame. Optional if can guess from image names")
    parser.add_argument('--height',default=None,type=int,help="Width dimension of frame. Optional if can guess from image names")
    parser.add_argument('--subdirs', default=False, action='store_true',help='If we should make snakes for subdirectories in snake_dir and output in subdirectories in image_dir')
    parser.add_argument('--subsubdirs', default=False, action='store_true',help='If subdirectories in snake_dir are two levels deep')
    parser.add_argument('-c','--colorful', action='store_true',help="Use different colors for each snake")
    parser.add_argument('--background_img_dir', default=None,type=readable_dir,help="Directory with images to use as backgrounds for TIFs")

    args = parser.parse_args()

    make_snake_images(
        args.snake_dir,
        args.image_dir,
        args.width,
        args.height,
        args.subdirs,
        args.subsubdirs,
        args.colorful,
        args.background_img_dir,
    )
