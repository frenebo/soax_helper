import cv2
import sys
import os

if __name__ == "__main__":
    print("usage: arguments are source image folder and target video name something.avi")
    image_folder = sys.argv[1]
    video_name = sys.argv[2]
    dir_contents = os.listdir(image_folder)
    dir_contents.sort()
    images = [img for img in dir_contents if img.endswith(".png")]
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_name, 0, 10, (width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    cv2.destroyAllWindows()
    video.release()
