import cv2
import sys
import os
import argparse
from snakeutils.files import readable_dir
from snakeutils.logger import PrintLogger, Colors

def write_vid_for_dir_images(image_folder,video_path,logger):
    if not video_path.endswith(".mp4"):
        logger.FAIL("Save video path {} should end with .mp4".format(video_path))

    dir_contents = os.listdir(image_folder)
    dir_contents.sort()
    images = [img for img in dir_contents if (img.endswith(".png") or img.endswith(".tif"))]
    if len(images) == 0:
        logger.error("No images found in {}".format(image_folder))
        return

    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape
    logger.log("dtype: ".format(str(frame.dtype)))

    video = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), 10, (width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    cv2.destroyAllWindows()
    video.release()

def make_video(image_folder,video_dir,use_subdirs,logger=PrintLogger):
    if use_subdirs:
        subdir_names = [name for name in os.listdir(image_folder) if os.path.isdir(os.path.join(image_folder,name))]

        logger.log("Making videos for image subdirectories {}".format(subdir_names))

        for subdir_name in subdir_names:
            subdir_path = os.path.join(image_folder,subdir_name)
            video_path = os.path.join(video_dir,subdir_name + ".mp4")
            write_vid_for_dir_images(subdir_path,video_path,logger)
    else:
        video_path = os.path.join(video_dir, "results.mp4")
        write_vid_for_dir_images(image_folder,video_path,logger)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('image_dir',type=readable_dir,help="Source directory to find graphed snakes")
    parser.add_argument('video_dir',type=readable_dir,help="Directory to save video(s)")
    parser.add_argument('--subdirs', default=False, action='store_true',help='If we should make snakes for subdirectories in snake_dir and output in subdirectories in image_dir')

    args = parser.parse_args()

    make_video(args.image_di,args.video_dir,args.subdirs)
