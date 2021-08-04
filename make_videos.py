import cv2
import sys
import os
import argparse
from snakeutils.files import readable_dir, has_one_of_extensions, find_files_or_folders_at_depth
from snakeutils.logger import PrintLogger, Colors

def write_vid_for_dir_images(image_folder,video_path,logger):
    if not video_path.endswith(".mp4"):
        logger.FAIL("Save video path {} should end with .mp4".format(video_path))

    dir_contents = os.listdir(image_folder)
    dir_contents.sort()
    images = [img for img in dir_contents if has_one_of_extensions(img, [".png", ".tif", ".tiff"])]
    if len(images) == 0:
        logger.error("No images found in {}".format(image_folder))
        return

    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape
    logger.log("  reading dtype from first frame: ".format(str(frame.dtype)))

    video = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), 10, (width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    cv2.destroyAllWindows()
    video.release()

def make_videos(root_image_dir,root_video_dir,source_images_depth,logger=PrintLogger):
    if source_images_depth == 0:
        video_path = os.path.join(root_video_dir, "results.mp4")
        write_vid_for_dir_images(root_image_dir,video_path,logger)
    else:
        image_dirs_depth = source_images_depth - 1
        image_dir_location_info = find_files_or_folders_at_depth(root_image_dir, image_dirs_depth, folders_not_files=True)
        for containing_dir, image_dir_name in image_dir_location_info:
            image_containing_dir_relpath = os.path.relpath(containing_dir, root_image_dir)
            video_containing_dirpath = os.path.join(root_video_dir, image_containing_dir_relpath)
            if not os.path.isdir(video_containing_dirpath):
                if os.path.exists(video_containing_dirpath):
                    logger.FAIL("Cannot save videos in {}: path exists but is not directory".format(video_containing_dirpath))
                else:
                    os.makedirs(video_containing_dirpath)
            image_dir_path = os.path.join(containing_dir, image_dir_name)
            video_path = os.path.join(video_containing_dirpath, image_dir_name + ".mp4")

            write_vid_for_dir_images(image_dir_path, video_path)

            logger.log("Making video for {}".format(image_dir_path))
            logger.log("  Saved video in {}".format(video_path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('image_dir',type=readable_dir,help="Source directory to find graphed snakes")
    parser.add_argument('video_dir',type=readable_dir,help="Directory to save video(s)")
    parser.add_argument('source_images_depth', default=0, type=int, help="How many subdirs deep to find source images (default 0)")
    # parser.add_argument('--subdirs', default=False, action='store_true',help='If we should make snakes for subdirectories in snake_dir and output in subdirectories in image_dir')

    args = parser.parse_args()

    make_videos(args.image_di,args.video_dir,args.source_images_dept)
