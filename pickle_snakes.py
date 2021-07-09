import sys
import os
from matplotlib import pyplot as plt
import numpy as np
from snakeutils.files import extract_snakes
import pickle
import argparsee

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('snakes_dir',help="Directory with snake text files")
    parser.add_argument('pickle_dir',help="Directory to save pickled snakes")

    args = parser.parse_args()

    dir_name = args.snakes_dir
    pickle_dir = args.pickle_dir
    filenames = os.listdir(dir_name)

    for filename in filenames:
        fp = os.path.join(dir_name,filename)

        with open(fp, "r") as snake_file:
            snakes = extract_snakes(snake_file)

            pickle_filename = "".join(filename.split(".")[:-1]) + ".pickle"
            pickle_fp = os.path.join(pickle_dir,pickle_filename)

            with open(pickle_fp, 'wb') as handle:
                pickle.dump(snakes, handle, protocol=pickle.HIGHEST_PROTOCOL)
