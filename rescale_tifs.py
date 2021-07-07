from snakeutils.files import readable_dir
import os
import argparse
import matplotlib.pyplot as plt

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('rescale_factor',type=float,help="Scale factor, for example 0.5 to make tifs half scale")
    parser.add_argument('source_dir',type=readable_dir,help="Directory where source tif files are")
    parser.add_argument('target_dir',type=readable_dir)

    args = parser.parse_args()

    tif_files = [filename for filename in os.listdir(args.source_dir) if filename.endswith(".tif")]

    for filename in tif_files:
        fp = os.path.join(args.source_dir,filename)
        with open(fp, 'rb') as tiff_file:
            img = plt.imread(tiff_file)
            print(img.shape)

