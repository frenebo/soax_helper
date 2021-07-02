import numpy as np
from matplotlib import pyplot as plt
import sys
import os
from snakeutils.files import extract_snakes
from scipy.spatial.distance import cdist
import math

def get_tip_coords_and_unit_vecs(snakes):
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

        start_dx = x[0] - x[1]
        start_dy = y[0] - y[1]
        start_norm = np.linalg.norm([start_dx,start_dy])
        start_unit_vec = [start_dx/start_norm,start_dy/start_norm]

        end_dx = x[-1] - x[-2]
        end_dy = y[-1] - y[-2]
        end_norm = np.linalg.norm([end_dx,end_dy])
        end_unit_vec = [end_dx/end_norm,end_dy/end_norm]

        tip_unit_vectors[snake_idx*2] = start_unit_vec
        tip_unit_vectors[snake_idx*2 + 1] = end_unit_vec

    return tip_coords,tip_unit_vectors

def local_match_snakes(snakes):
    # threshold for matching tips is d*e^angle < eta
    eta = 10
    angle_threshold = np.pi/4

    # we want an array that looks like:
    # [
    #    [snake0_startx,snake0_starty],
    #    [snake0_endx,snake0_endy],
    #    [snake1_startx,snake1_starty],
    #    [snake1_endx,snake1_endy],
    #    etc...
    # ]

    tip_coords,tip_unit_vecs = get_tip_coords_and_unit_vecs(snakes)

    # 2n x 2n matrix of distances from each start and end of a snake to every other start/end
    tip_dists = cdist(tip_coords,tip_coords)

    # index pairs referring to distance between same points, index pairs of start and end of same snake
    for x in range(len(snakes)):
        tip_dists[2*x,2*x] = np.Inf
        tip_dists[2*x,2*x+1] = np.Inf
        tip_dists[2*x+1,2*x+1] = np.Inf
        tip_dists[2*x+1,2*x] = np.Inf

    # Since we look for tips matching with d*e^theta < eta, we can rule out
    # indices where d >= eta
    match_candidates = np.transpose((tip_dists < eta).nonzero())
    print("candidates length")
    print(match_candidates)
    print(match_candidates.shape)

    matches = []

    for candidate in match_candidates:
        tip1_idx = candidate[0]
        tip2_idx = candidate[1]

        tip1_snake_idx = math.floor(tip1_idx/2)
        tip1_type = "start" if tip1_idx % 2 == 0 else "end"
        tip2_snake_idx = math.floor(tip2_idx/2)
        tip2_type = "start" if tip2_idx % 2 == 0 else "end"

        tip1_unit_vec = tip_unit_vecs[tip1_idx]
        tip2_unit_vec = tip_unit_vecs[tip2_idx]

        # subract arccos from np.pi because we want tips pointing in opposite
        # direction to have zero angle
        angle = np.pi -  np.arccos(np.dot(tip1_unit_vec,tip2_unit_vec))
        print("tip1: pos ({},{}) direction ({},{}) tip2: pos ({},{}) direction ({},{}) dist: {} angle: {}".format(
                tip_coords[tip1_idx][0],
                tip_coords[tip1_idx][1],
                tip1_unit_vec[0],
                tip1_unit_vec[1],
                tip_coords[tip2_idx][0],
                tip_coords[tip2_idx][1],
                tip2_unit_vec[0],
                tip2_unit_vec[1],
                tip_dists[tip1_idx][tip2_idx],
                angle
                ))
        score = tip_dists[tip1_idx][tip2_idx] * np.exp(angle)

        if score < eta and angle < angle_threshold:
            matches.append(candidate)

    print("candidates number: {}".format(len(match_candidates)))
    print("matches number: {}".format(len(matches)))

    seen_tips = []

    for i in range(min(1000,len(matches))):
        tip1_idx = matches[i][0]
        tip2_idx = matches[i][1]

        snake1_idx = math.floor(tip1_idx/2)
        snake2_idx = math.floor(tip2_idx/2)

        tip1_duplicate = tip1_idx in seen_tips
        tip2_duplicate = tip2_idx in seen_tips

        seen_tips.append(tip1_idx)
        seen_tips.append(tip2_idx)

        # print(snakes[snake1_idx].shape)
        snake1x,snake1y = snakes[snake1_idx].T
        snake2x,snake2y = snakes[snake2_idx].T
        plt.plot(snake1x,snake1y,linewidth=(0.5 if tip1_duplicate else 0.1))
        plt.plot(snake2x,snake2y,linewidth=(0.5 if tip2_duplicate else 0.1))
        print(snake1x,snake1y)

    plt.axes().set_aspect('equal', adjustable='box')
    plt.axis([0,2304,2304,0])
    plt.xlabel("x")
    plt.ylabel("y")
    plt.savefig("data/match",dpi=500)
    plt.clf()

        # print(tip1_snake_idx)
        # print(tip1_type)
        # print(tip2_snake_idx)
        # print(tip2_type)


if __name__ == "__main__":
    print("arguments: directory of 2D snakes")
    if len(sys.argv) < 2:
        raise Exception("Missing argument")
    snake_dir = sys.argv[1]
    snake_filenames = os.listdir(snake_dir)
    snake_filenames = [filename for filename in snake_filenames if filename.endswith(".txt")]
    snake_filenames.sort()

    for snake_fn in snake_filenames:
        snake_fp = os.path.join(snake_dir,snake_fn)
        with open(snake_fp, "r") as snake_file:
            snakes = extract_snakes(snake_file)
            local_match_snakes(snakes)
        raise Exception("finished first, stopping now")

