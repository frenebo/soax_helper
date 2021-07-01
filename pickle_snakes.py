import sys
import os
from matplotlib import pyplot as plt
import numpy as np
from snakeutils.files import extract_snakes
import pickle

if __name__ == "__main__":
    print("usage: 2 arguments: directory with snake text files, directory to save pickled snakes")

    dir_name = sys.argv[1]
    pickle_dir = sys.argv[2]
    filenames = os.listdir(dir_name)

    for filename in filenames:
        fp = os.path.join(dir_name,filename)

        with open(fp, "r") as snake_file:
            snakes = extract_snakes(snake_file)

            pickle_filename = "".join(filename.split(".")[:-1]) + ".pickle"
            pickle_fp = os.path.join(pickle_dir,pickle_filename)

            with open(pickle_fp, 'wb') as handle:
                pickle.dump(snakes, handle, protocol=pickle.HIGHEST_PROTOCOL)
