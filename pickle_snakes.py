import sys
import os
from matplotlib import pyplot as plt
import numpy as np
from snakeutils.files import extract_snakes, run_fast_scandir
import pickle
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('snakes_dir',help="Directory with snake text files")
    parser.add_argument('pickles_dir',help="Directory to save pickled snakes")

    args = parser.parse_args()

    dir_name = args.snakes_dir
    pickles_dir = args.pickles_dir

    subfolders, text_filepaths = run_fast_scandir(dir_name,[".txt"])

    for text_fp in text_filepaths:
        relative_fp = os.path.relpath(text_fp,dir_name)
        relative_dir = os.path.dirname(relative_fp)

        with open(text_fp, 'r') as snake_file:
            snakes = extract_snakes(snake_file)

        # remove .txt and add .pickle
        pickle_relative_fp = relative_fp[:-4] + ".pickle"
        pickle_fp = os.path.join(pickles_dir,pickle_relative_fp)
        new_pickle_dir = os.path.dirname(pickle_fp)

        if not os.path.exists(new_pickle_dir):
            os.makedirs(new_pickle_dir)

        with open(pickle_fp, 'wb') as handle:
            pickle.dump(snakes, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # filenames = os.listdir(dir_name)
    # filenames.sort()

    # for filename in filenames:
    #     fp = os.path.join(dir_name,filename)

    #     with open(fp, "r") as snake_file:
    #         print(fp)
    #         snakes = extract_snakes(snake_file)

    #         pickle_filename = "".join(filename.split(".")[:-1]) + ".pickle"
    #         pickle_fp = os.path.join(pickle_dir,pickle_filename)

    #         with open(pickle_fp, 'wb') as handle:
    #             pickle.dump(snakes, handle, protocol=pickle.HIGHEST_PROTOCOL)
