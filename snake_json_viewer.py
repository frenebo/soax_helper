import argparse

from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from snakeutils.tifimage import pil_img_3d_to_np_arr
from PIL import Image

from snakeutils.snakejson import load_json_snakes

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='JSON snake viewer')
    parser.add_argument("json_path")
    parser.add_argument('--flatten',default=False,action='store_true',help="Plot in 2D")
    parser.add_argument('--background',default=None,help="TIF to graph in background")

    args = parser.parse_args()

    snakes,metadata = load_json_snakes(args.json_path)

    fig = plt.figure(num=args.json_path, figsize=(10,7))
    # fig.sets
    if args.flatten:
        ax = plt.axes()
        ax.set_xlim(0,metadata["dims_pixels_xyz"][0])
        ax.set_ylim(0,metadata["dims_pixels_xyz"][1])
    else:
        ax = plt.axes(projection="3d")
        ax.set_xlim(0,metadata["dims_pixels_xyz"][0])
        ax.set_ylim(0,metadata["dims_pixels_xyz"][1])
        ax.set_zlim(0,metadata["dims_pixels_xyz"][2])

    if args.background is not None:
        if not args.flatten:
            raise Exception("Background only supported with 2D graph")
        pil_img = Image.open(args.background)
        np_arr = pil_img_3d_to_np_arr(pil_img)
        # take slice
        np_arr = np_arr[:,:,0]
        plt.imshow(np_arr, cmap='gray')


    for snake_info in snakes:
        x = []
        y = []
        z = []
        for snake_pt in snake_info:
            pt_x,pt_y,pt_z = snake_pt["pos"]
            x.append(pt_x)
            y.append(pt_y)
            z.append(pt_z)
        if args.flatten:
            ax.plot(x,y, 'b')
        else:
            ax.plot(x,y,z, 'b')
    plt.show()