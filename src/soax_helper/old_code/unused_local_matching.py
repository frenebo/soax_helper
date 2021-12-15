import numpy as np
from matplotlib import pyplot as plt
from scipy.spatial.distance import cdist
import math

def get_tip_coords_and_unit_vecs(snakes):
    tip_coords = np.zeros( [len(snakes)*2,2] )
    tip_unit_vectors = np.zeros( [len(snakes)*2,2])

    for snake_idx,snake in enumerate(snakes):
        x,y=snake.T[:2]

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

# The distance at coordinates x,y is the same distance at coordinates y,x, so we might as well
# set all the values along the diagonal and below it to infinity. Distances along diagonal
# are just distances from one point to itself, so they should be zero
def redundant_tip_dists_as_infinity(tip_dists):
    infinity_except_below_diag = np.ones(tip_dists.shape)*np.Inf
    return tip_dists + infinity_except_below_diag

# We want the distances between the start and end tips of the same snake to be zero
def distances_between_same_snake_tips_as_infinity(tip_dists):
    # make copy so we don't change the original array
    tip_dists = np.array(tip_dists)

    # index pairs referring to distance between same points, index pairs of start and end of same snake
    for x in range(len(snakes)):
        tip_dists[2*x,2*x] = np.Inf
        tip_dists[2*x,2*x+1] = np.Inf
        tip_dists[2*x+1,2*x+1] = np.Inf
        tip_dists[2*x+1,2*x] = np.Inf

    return tip_dists

def local_match_snakes(snakes):
    #
    distance_threshold = 10
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
    tip_dists = redundant_dists_as_infinity(tip_dists)
    tip_dists = distances_between_same_snake_tips_as_infinity(tip_dists)

    # We look for tip pairs whose distances are less than eta
    match_candidates = np.transpose((tip_dists < distance_threshold).nonzero())



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

        score = tip_dists[tip1_idx][tip2_idx] * np.exp(angle)

        if score < eta and angle < angle_threshold:
            matches.append(candidate)

    print("candidates number: {}".format(len(match_candidates)))
    print("matches number: {}".format(len(matches)))

    tip_matches = {}

    for i in range(len(matches)):
        tip1_idx = matches[i][0]
        tip2_idx = matches[i][1]

        snake1_idx = math.floor(tip1_idx/2)
        snake2_idx = math.floor(tip2_idx/2)

        match_data = {
            "snake1": snake1_idx,
            "snake2": snake2_idx,
            "tip1type": "start" if tip1_idx % 2 == 0 else "end",
            "tip2type": "start" if tip2_idx % 2 == 0 else "end",
            "dist": tip_dists[tip1_idx][tip2_idx]
        }

        if tip1_idx in tip_matches:
            tip_matches[tip1_idx].append(match_data)
        else:
            tip_matches[tip1_idx] = [match_data]

        if tip2_idx in tip_matches:
            tip_matches[tip2_idx].append(match_data)
        else:
            tip_matches[tip2_idx] = [match_data]

        snake1x,snake1y = snakes[snake1_idx].T[:2]
        snake2x,snake2y = snakes[snake2_idx].T[:2]
        plt.plot(snake1x,snake1y,linewidth=0.1)
        plt.plot(snake2x,snake2y,linewidth=0.1)

    print("{} tip matches".format(len(tip_matches)))
    print(tip_matches)

