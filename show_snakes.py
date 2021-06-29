import sys
import os
from matplotlib import pyplot as plt
import numpy as np

def extract_snakes(snake_file,filename):
    # get past starting params
    count = 0
    while count < 30:
        snake_file.readline()
        count += 1

    snake_dict = {}
    done = False
    lines = [line.strip().split() for line in snake_file]

    line_idx = 0
    snake_name = None
    snake_points = None
    while True:
        # if snake name is none, last iteration just finished a snake
        if snake_name is None:
            line = lines[line_idx]
            #reached junction point section
            if len(line) == 3:
                break

            snake_name = line[0]
            snake_points = []

        line = lines[line_idx]
        # if reached a new label for snake or reached junction section of file
        if len(line) == 1 or len(line) == 3:
            snake_dict[snake_name] = snake_points
            snake_name = None
            snake_points = None

            #reached junction section
            if len(line) == 3:
                break
            #reached end of file
            if line_idx >= len(lines):
                break
            if len(line) == 1:
                # skip open/closed #1 #0 line
                line_idx += 1

            continue
        else:
##            print(line)
##            print(filename)
            x= float(line[2])
            y= float(line[3])
            snake_points.append([x,y])

            line_idx += 1
            continue

    return snake_dict



if __name__ == "__main__":
    print("usage: 2 arguments: directory with snake text files, directory to save images")

    dir_name = sys.argv[1]
    image_dir_name = sys.argv[2]
    filenames = os.listdir(dir_name)

    for filename in filenames:
        fp = os.path.join(dir_name,filename)

        with open(fp, "r") as snake_file:
            snakes = extract_snakes(snake_file,filename)
            plt.gca().invert_yaxis()
            for snake_name, snake_pts in snakes.items():
##                print(snake_pts)
##                print(snake_name)
                snake_pts = np.array(snake_pts)
##                print(snake_pts.shape)
##                for pt in snake_pts:
##                    print("({},{})".format(pt[0],pt[1]),end="")
                x,y = snake_pts.T
##                print(x.shape)
##                print(y.shape)
                # plt.plot(x,y,'b')
                plt.plot(x,y)

            # some_snakefile.tif => some_snakefile.jpg
            save_img_filename = "".join(filename.split(".")[:-1]) + ".png"
            save_img_fp = os.path.join(image_dir_name,save_img_filename)
            plt.savefig(save_img_fp)
            # clear figure so we can do the next plot
            plt.clf()

