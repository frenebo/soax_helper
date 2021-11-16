import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
import argparse
import os
from mpl_toolkits.mplot3d import Axes3D
from snakeutils.files import find_files_or_folders_at_depth
from matplotlib.backends.backend_tkagg import (
                                    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from snakeutils.params import param_filename_tags
from snakeutils.snakejson import load_json_snakes

param_names_by_tags = {v: k for k, v in param_filename_tags.items()}

def parse_fn_param_str(param_str):
    best_tag_match = None
    for tag in param_names_by_tags:
        if param_str.startswith(tag) and (best_tag_match is None or len(tag) > len(best_tag_match)):
            best_tag_match = tag
            # print("new bestmatch is {}".format(tag))

    if best_tag_match is None:
        raise Exception("Could not find param name tag in filename parameter section '{}'".format(param_str))

    # return
    param_name = param_names_by_tags[best_tag_match]
    # print(param_names_by_tags)
    # print("param name: {}".format(param_name))
    param_val = param_str[len(best_tag_match):]

    return param_name, param_val

def parse_param_folder_name(folder_name):
    start_string = "params_"
    if not folder_name.startswith(start_string):
        raise Exception("Expected folder {} to start with 'params' - in order to parse and view snakes")
    folder_name = folder_name[len(start_string):]
    param_strings = folder_name.split('_')

    param_values = []

    for param_str in param_strings:
        param_name, param_val = parse_fn_param_str(param_str)
        param_values.append( (param_name, param_val) )

    return param_values

def make_gui(
    root_folder,
    param_ranges,
    param_defaults,
    param_vals_by_foldername,
    image_json_names,
    flatten=False):
    root = tk.Tk()
    # root.wm_title("Embedding in Tk")

    fig = Figure(figsize=(5, 4), dpi=100)

    canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
    canvas.draw()

    if flatten:
        ax = fig.add_subplot(111)
    else:
        ax = fig.add_subplot(111, projection="3d")

    def show_snakes(snakes):
        ax.clear()
        for snake in snakes:
            X = []
            Y = []
            Z = []
            for pt in snake:
                X.append(pt["pos"][0])
                Y.append(pt["pos"][1])
                Z.append(pt["pos"][2])
            if flatten:
                ax.plot(X,Y)
            else:
                ax.plot(X,Y,Z)
        canvas.draw()

    def show_selected_snakes(*args):
        selected_params = {}
        for key, tk_str_val in param_tk_string_vars.items():
            selected_params[key] = tk_str_val.get()

        selected_param_folder = None
        for foldername, folder_params in param_vals_by_foldername.items():
            matching = True
            for param_name, param_val in folder_params:
                if selected_params[param_name] != param_val:
                    matching = False

            if matching:
                selected_param_folder = foldername
        if selected_param_folder is None:
            raise Exception("Could not find parameter folder with parameters {}".format(selected_params))

        img_idx = selected_img_var.get()
        folder_path = os.path.join(root_folder, selected_param_folder)
        # contents = os.listdir(folder_path)
        # contents.sort()
        json_path = os.path.join(folder_path, image_json_names[img_idx])

        if not os.path.exists(json_path):
            raise Exception("Expected to find file {}, does not exist".format(json_path))

        print("Showing {}".format(json_path))
        root.wm_title(json_path)

        snakes, metadata = load_json_snakes(json_path)
        show_snakes(snakes)

    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()

    params_frame = tk.Frame(root)
    param_tk_string_vars = {}

    for (param_name, param_vals) in param_ranges:
        param_buttons_frame = tk.Frame(params_frame)
        tk.Label(param_buttons_frame, text=param_name).pack(side=tk.TOP)
        param_tk_var = tk.StringVar(root, param_defaults[param_name])
        param_tk_string_vars[param_name] = param_tk_var
        param_tk_var.trace_add("write", show_selected_snakes)

        for param_val in param_vals:
            tk.Radiobutton(
                param_buttons_frame,
                text=param_val,
                variable=param_tk_var,
                value=param_val).pack(side=tk.TOP,ipady=0)

        param_buttons_frame.pack(side=tk.RIGHT, padx=0, pady=0)

    selected_img_var = tk.IntVar(root, 0)
    image_selector_frame = tk.Frame(params_frame)
    tk.Label(image_selector_frame, text="Image").pack(side=tk.TOP)
    tk.Scale(image_selector_frame, from_=0, to=(len(image_json_names)-1), variable=selected_img_var, orient=tk.HORIZONTAL).pack(side=tk.TOP,ipady=0)
    image_selector_frame.pack(side=tk.RIGHT,padx=0,pady=0)

    params_frame.pack(side=tk.TOP)

    selected_img_var.trace_add("write", show_selected_snakes)

    show_selected_snakes()

    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    tk.mainloop()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='JSON snake viewer')
    parser.add_argument("jsons_dir")
    parser.add_argument('--flatten',default=False,action='store_true',help="Plot in 2D")
    # parser.add_argument('--background',default=None,help="TIF to graph in background")

    args = parser.parse_args()

    jsons_folders_files = find_files_or_folders_at_depth(args.jsons_dir, 1, file_extension=".json")
    # Assume image json filenames are same for all folders
    image_json_names = [fn for folder,fn in find_files_or_folders_at_depth(jsons_folders_files[0][0], 0, file_extension=".json")]

    # print(jsons_folders_files)
    # varied_params = {}
    # varied_params = []
    if len(jsons_folders_files) == 0:
        raise Exception("Could not find any json files in subdirectories in {}".format(args.jsons_dir))

    first_param_vals = parse_param_folder_name(os.path.split(jsons_folders_files[0][0])[1])

    param_ranges = [(param_name, []) for param_name, param_val in first_param_vals]
    # For param selection menu, defaults are the values in the first param folder name
    param_defaults = {param_name:param_val for param_name, param_val in first_param_vals}

    param_vals_by_foldername = {}

    for (folder_path, image_json_name) in jsons_folders_files:
        __, param_folder = os.path.split(folder_path)
        # print(param_folder)
        folder_param_vals = parse_param_folder_name(param_folder)
        param_vals_by_foldername[param_folder] = folder_param_vals
        for i, (param_name, param_val) in enumerate(folder_param_vals):
            if param_val not in param_ranges[i][1]:
                param_ranges[i][1].append(param_val)

    # Sort parameter values alphanumerically
    param_ranges = [(param_name, sorted(p_range)) for (param_name, p_range) in param_ranges]

    print(param_ranges)
    print(param_defaults)
    print(param_vals_by_foldername)
    print(image_json_names)

    make_gui(
        args.jsons_dir,
        param_ranges,
        param_defaults,
        param_vals_by_foldername,
        image_json_names,
        flatten=args.flatten)
