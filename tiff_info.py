import argparse
from snakeutils.files import readable_dir
import os
from PIL import Image
import numpy as np
from snakeutils.logger import PrintLogger

def tif_file_or_dir(target_path):
    try:
        dir_path = readable_dir(target_path)
        dir_contents = os.listdir(dir_path)
        tif_filenames = [filename for filename in dir_contents if filename.endswith(".tif")]
        tif_filepaths = [os.path.join(target_path,tif_fn) for tif_fn in tif_filenames]
        return tif_filepaths

    except argparse.ArgumentTypeError:
        if not target_path.endswith(".tif"):
            raise argparse.ArgumentTypeError("{} is not a directory or tif file".format(target_path))

        if not os.path.exists(target_path):
            raise argparse.ArgumentTypeError("{} does not exist".format(target_path))

        return [target_path]

def readable_dir(dirpath):
    if not os.path.isdir(dirpath):
        raise argparse.ArgumentTypeError("{} is not a directory".format(dirpath))

    return dirpath

def tiff_info(tif_paths,logger=PrintLogger):
    for tif_path in tif_paths:
        data = Image.open(tif_path)
        shape = data.size
        stack_height = data.n_frames
        arr = np.array(data)
        dtype = str(arr.dtype)

        logger.log("{}:".format(tif_path))
        logger.log(" shape: {}, stack frames: {}, dtype: {}".format(shape,stack_height,dtype))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get info from tif file or directory of tif files')
    parser.add_argument('target',type=tif_file_or_dir,help="TIF file or directory of tif files")

    args = parser.parse_args()

    tiff_info(args.target)