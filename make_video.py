import cv2
import sys
import os
import argparse
from snakeutils.files import readable_dir

def make_and_write_vid(image_folder,video_path):
    dir_contents = os.listdir(image_folder)
    dir_contents.sort()
    images = [img for img in dir_contents if (img.endswith(".png") or img.endswith(".tif"))]
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_path, 0, 10, (width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    cv2.destroyAllWindows()
    video.release()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('image_dir',type=readable_dir,help="Source directory to find graphed snakes")
    parser.add_argument('video_dir',help="Directory to save video(s)")
    parser.add_argument('--subdirs', default=False, action='store_true',help='If we should make snakes for subdirectories in snake_dir and output in subdirectories in image_dir')

    args = parser.parse_args()

    image_folder = args.image_dir
    video_dir = args.video_dir

    if args.subdirs:
        subdir_names = [name for name in os.listdir(image_folder) if os.path.isdir(os.path.join(dir_name,name))]

        print("Making videos for image subdirectories {}".format(subdir_names))

        for subdir_name in subdir_names:
            subdir_path = os.path.join(image_folder)
            video_path = os.path.join(video_dir,subdir_name + ".avi")
            make_and_write_vid(subdir_path,video_path)
    else:
        video_path = os.path.join(video_dir, "results.avi")
        make_and_write_vid(image_folder,video_path)
