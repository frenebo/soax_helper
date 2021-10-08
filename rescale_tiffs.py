from snakeutils.files import has_one_of_extensions
from snakeutils.tifimage import save_3d_tif, tiff_img_3d_to_arr
from skimage.transform import resize
import os
# import argparse
import matplotlib.pyplot as plt
import imageio
import cv2
from PIL import Image
from scipy.ndimage import zoom
import tifffile
import numpy as np
from snakeutils.logger import PrintLogger

def rescale_tiffs(
    batch_resample_path,
    source_tiff_dir,
    temp_dir,
    target_tiff_dir,
    xy_factor,
    z_factor,
    logger=PrintLogger,
    ):
    raise Exception("Not Implemented")
    # pass