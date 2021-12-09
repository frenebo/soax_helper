import argparse
import vedo
import numpy as np
import os
from PIL import Image
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker

from .snakeutils.files import find_files_or_folders_at_depth
from .snakeutils.tifimage import pil_img_3d_to_np_arr

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Split 3D Tiff into its 2D frames')
    parser.add_argument('tubes')
    parser.add_argument('beads')

    args = parser.parse_args()

    tubes_folder_and_files = find_files_or_folders_at_depth(args.tubes, 0, file_extensions=[".tif", ".tiff"])
    beads_folder_and_files = find_files_or_folders_at_depth(args.beads, 0, file_extensions=[".tif", ".tiff"])

    plt.figure(figsize=(15, 15), dpi=80)

    print([element[1] for element in tubes_folder_and_files])
    object_num = min(len(tubes_folder_and_files), len(beads_folder_and_files))
    for i in range(object_num):
        tube_path = os.path.join(*tubes_folder_and_files[i])
        bead_path = os.path.join(*beads_folder_and_files[i])

        tube_pil_img = Image.open(tube_path)
        bead_pil_img = Image.open(bead_path)
        tube_arr = pil_img_3d_to_np_arr(tube_pil_img)
        bead_arr = pil_img_3d_to_np_arr(bead_pil_img)
        bead_arr = bead_arr * 0.75
        # print(tube_arr.shape)
        # print(bead_arr.shape)
        combined_arr = np.maximum(tube_arr[:,:,:10], bead_arr[:,:,:10])
        projection = np.amax(combined_arr, 2)

        ax = plt.gca()
        ax.xaxis.set_major_locator(ticker.MultipleLocator(40))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(40))
        plt.imshow(projection, cmap='gray')
        print("Saving projection of {} and {} sices".format(tube_path, bead_path))
        plt.savefig("frame{}.jpeg".format(i), bbox_inches='tight')
        plt.clf()

        # im = Image.fromarray(projection)
        # im = im.convert('RGB')
        # im.save("frame{}.jpeg".format(i))
        # # vol
        # where_beads_brighter = bead_arr > tube_arr
        # tube_arr[bead_arr > tube_arr] =

        # print(tubes_folder_and_files[0][1])
        # # first_tube_path = os.path.join(tubes_folder_and_files[0][0], tubes_folder_and_files[0][1])
        # threedee = np.zeros((projection.shape[0],projection.shape[1], 1),dtype=projection.dtype)
        # threedee[:,:,0] = projection
        # vol = vedo.Volume(threedee)
        # vedo.show(vol, axes=1, viewup='y')
        # exit()

    # vol = vedo.Volume('cell.tif')
    # vedo.show(vol, axes=1, viewup='z')