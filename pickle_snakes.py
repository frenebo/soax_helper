import sys
import os
from matplotlib import pyplot as plt
import numpy as np
from snakeutils.files import extract_snakes, run_fast_scandir
import pickle
import argparse
from snakeutils.logger import PrintLogger, Colors

def pickle_snakes(dir_name,pickles_dir,logger=PrintLogger):
    subfolders, text_filepaths = run_fast_scandir(dir_name,[".txt"])

    for text_fp in text_filepaths:
        relative_fp = os.path.relpath(text_fp,dir_name)
        relative_dir = os.path.dirname(relative_fp)

        logger.log("Loading snakes from {}".format(text_fp))
        with open(text_fp, 'r') as snake_file:
            snakes = extract_snakes(snake_file)

        # remove .txt and add .pickle
        pickle_relative_fp = relative_fp[:-4] + ".pickle"
        pickle_fp = os.path.join(pickles_dir,pickle_relative_fp)
        new_pickle_dir = os.path.dirname(pickle_fp)

        if not os.path.exists(new_pickle_dir):
            os.makedirs(new_pickle_dir)
            logger.log("  Created directory {}".format(new_pickle_dir))
        logger.log("  Saving snake pickle in {}".format(pickle_fp), Colors.YELLOW)
        with open(pickle_fp, 'wb') as handle:
            pickle.dump(snakes, handle, protocol=pickle.HIGHEST_PROTOCOL)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('snakes_dir',help="Directory with snake text files")
    parser.add_argument('pickles_dir',help="Directory to save pickled snakes")

    args = parser.parse_args()
