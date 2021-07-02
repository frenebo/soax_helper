import numpy as np
from matplotlib import pyplot as plt
import sys
import os
from snakeutils.files import extract_snakes
from scipy.spatial.distance import cdist
import math

def local_match_snakes(snakes):
    # threshold for matching tips is d*e^angle < eta
    eta = 10

    # we want an array that looks like:
    # [
    #    [snake0_startx,snake0_starty],
    #    [snake0_endx,snake0_endy],
    #    [snake1_startx,snake1_starty],
    #    [snake1_endx,snake1_endy],
    #    etc...
    # ]
    tip_coords = np.zeros( [len(snakes)*2,2] )
    tip_unit_vectors = np.zeros( [len(snakes)*2,2])

    for snake_idx,snake in enumerate(snakes):
        x,y=snake.T

        start_x = x[0]
        start_y = y[0]
        end_x = x[-1]
        end_y = y[-1]

        tip_coords[snake_idx*2] = [start_x,start_y]
        tip_coords[snake_idx*2 + 1] = [end_x,end_y]

        start_dx = x[1] - x[0]
        start_dy = y[1] - y[0]
        start_norm = np.linalg.norm([start_dx,start_dy])
        start_unit_vec = [start_dx/start_norm,start_dy/start_norm]

        end_dx = x[-1] - x[-2]
        end_dy = y[-1] - y[-2]
        end_norm = np.linalg.norm([end_dx,end_dy])
        end_unit_vec = [end_dx/end_norm,end_dy/end_norm]

        tip_unit_vectors[snake_idx*2] = start_unit_vec
        tip_unit_vectors[snake_idx*2 + 1] = end_unit_vec


    # plt.axes().set_aspect('equal', adjustable='box')
    # plt.axis([0,2304,2304,0])
    # plt.xlabel("x")
    # plt.ylabel("y")
    # start_x,start_y = tip_coords[0]
    # end_x,end_y = tip_coords[1]
    # print("Start: {},{}".format(start_x,start_y))
    # print("End: {},{}".format(end_x,end_y))
    # plt.plot([start_x,end_x],[start_y,end_y])
    # x,y = snakes[0].T
    # plt.plot(x,y)
    # plt.savefig("endpts")


    # flattened_ignore_indices = np.unravel_index(same_snake_positions, [2*len(snakes),2*len(snakes)])
    # test_stuff = np.zeros([2*len(snakes),2*len(snakes)])
    # test_stuff.put(
    #     flattened_ignore_indices,
    #     np.full([len(flattened_ignore_indices)],1),
    # )
    # print("Ignore indices:")
    # print(flattened_ignore_indices.shape)
    # print(flattened_ignore_indices[:20])
    # print("Test stuff:")
    # print(test_stuff[:10,:10])

    tip_dists = cdist(tip_coords,tip_coords)
    print("{} snakes".format(len(snakes)))
    print(tip_dists.shape)

    # index pairs referring to distance between same points, index pairs of start and end of same snake
    for x in range(len(snakes)):
        tip_dists[2*x,2*x] = np.Inf
        tip_dists[2*x,2*x+1] = np.Inf
        tip_dists[2*x+1,2*x+1] = np.Inf
        tip_dists[2*x+1,2*x] = np.Inf
    # same_snake_positions = ([[2*x,2*x] for x in range(len(snakes))] +
    #                         [[2*x,2*x + 1] for x in range(len(snakes))] +
    #                         [[2*x + 1,2*x] for x in range(len(snakes))] +
    #                         [[2*x + 1,2*x + 1] for x in range(len(snakes))])
    print(tip_dists[:4][:4])
    print(tip_dists[0][0])
    print(tip_dists[1][0])
    print(tip_dists[1][1])
    print(tip_dists[0][1])
    print(tip_dists[2][2])
    print(tip_dists[2][3])
    print(tip_dists[3][2])
    print(tip_dists[3][3])


if __name__ == "__main__":
    print("arguments: directory of 2D snakes")
    if len(sys.argv) < 2:
        raise Exception("Missing argument")
    snake_dir = sys.argv[1]
    snake_filenames = os.listdir(snake_dir)
    snake_filenames = [filename for filename in snake_filenames if filename.endswith(".txt")]
    snake_filenames.sort()

    print(snake_filenames)
    print("asdfdsadffsdf")

    for snake_fn in snake_filenames:
        print(snake_fn)
        snake_fp = os.path.join(snake_dir,snake_fn)
        with open(snake_fp, "r") as snake_file:
            snakes = extract_snakes(snake_file)
            local_match_snakes(snakes)
        raise Exception("finished first, stopping now")

