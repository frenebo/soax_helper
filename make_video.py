import cv2
import sys
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('image_dir',type=readable_dir,help="Source directory to find graphed snakes")
    parser.add_argument('video_path',help="Path to save video")
    parser.add_argument('-c','--colorful', action='store_true',help="Use different colors for each snake")

    args = parser.parse_args()

    image_folder = args.image_dir
    video_path = args.video_path
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
