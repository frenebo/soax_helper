from snakeutils.files import readable_dir
import os
import argparse
import matplotlib.pyplot as plt
import tifffile
import skimage

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('rescale_factor',type=float,help="Scale factor, for example 0.5 to make tifs half scale")
    parser.add_argument('source_dir',type=readable_dir,help="Directory where source tif files are")
    parser.add_argument('target_dir',type=readable_dir)

    args = parser.parse_args()

    if args.rescale_factor <= 0:
        raise Exception("Rescale factor must be positive")

    tif_files = [filename for filename in os.listdir(args.source_dir) if filename.endswith(".tif")]

    for filename in tif_files:
        fp = os.path.join(args.source_dir,filename)

        img = tifffile.imread(fp)

        dims = img.shape
        new_dims = []
        for dim in dims:
            new_dim = dim * args.rescale_factor
            if new_dim == 0:
                raise Exception("Dimension {} in {} rescaled by factor {} becomes zero".format(dim,fp,args.rescale_factor))
            new_dims.push(new_dim)

        resized_img = skimage.transform.resize(img, new_dims)
        new_fp = os.path.join(args.target_dir, "resized_" + filename)

        tifffile.imwrite(new_fp, resized_img, planarconfig='CONTIG')

