import numpy as np
from matplotlib import pyplot as plt
import sys
import os
from snakeutils.files import extract_snakes

def local_match_snakes

if __name__ == "__main__":
    print("arguments: directory of 2D snakes")
    if len(sys.argv) < 2:
        raise Exception("Missing argument")
    snake_dir = sys.argv[1]
    snake_filenames = os.listdir(image_folder)
    snake_filenames = [filename for filename in snake_filenames if filename.endswith(".txt")]
    snake_filenames.sort()

    for snake_fn in snake_filenames:
        snake_fp = os.path.join(snake_dir,snake_fn))
        with open(snake_fp, "r") as snake_file:
            snakes = extract_snakes(snake_file)

