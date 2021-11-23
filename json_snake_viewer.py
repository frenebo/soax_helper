import argparse
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from snakeutils.tifimage import pil_img_3d_to_np_arr
from PIL import ImageTk, Image
import tkinter as tk

from snakeutils.snakejson import load_json_snakes

def _image_scale_to_fit_in_box(pil_img, new_width, new_height):
    horizontal_ratio = new_width/pil_img.width
    vertical_ratio = new_height/pil_img.height

    zoom_factor = min(horizontal_ratio, vertical_ratio)

    return zoom_factor

class AnnotatorGui:
    def __init__(self):
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width = 300, height = 300)
        self.canvas.pack()
        self.root.update()

        pass


    def show_image(self, pil_image):
        zoom_factor = _image_scale_to_fit_in_box(pil_image, self.canvas.winfo_width(), self.canvas.winfo_height())

        pil_image = pil_image.resize([int(zoom_factor*s) for s in pil_image.size], Image.ANTIALIAS)

        tk_img = ImageTk.PhotoImage(pil_image)
        # self.current_image = tk_

        self.canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)
        self.root.update()

def display_snakes(snakes):
    # plt.clf()
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
    plt.pause(0.0001)

def test_thing(pil_img):
    gui = AnnotatorGui()
    gui.show_image(pil_img)
    gui.root.mainloop()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='JSON snake viewer')
    parser.add_argument("json_path")
    parser.add_argument('--flatten',default=False,action='store_true',help="Plot in 2D")
    parser.add_argument('--background',default=None,help="TIF to graph in background")

    args = parser.parse_args()

    snakes,metadata = load_json_snakes(args.json_path)

    fig = plt.figure(num=args.json_path, figsize=(10,7))

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

    print(len(snakes))

    display_snakes(snakes)
    # for snake_info in snakes:
    #     x = []
    #     y = []
    #     z = []
    #     for snake_pt in snake_info:
    #         pt_x,pt_y,pt_z = snake_pt["pos"]
    #         x.append(pt_x)
    #         y.append(pt_y)
    #         z.append(pt_z)
    #     if args.flatten:
    #         ax.plot(x,y, 'b')
    #     else:
    #         ax.plot(x,y,z, 'b')