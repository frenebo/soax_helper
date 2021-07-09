from snakeutils.files import readable_dir
import os
import argparse
import matplotlib.pyplot as plt
import imageio
import cv2

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('rescale_factor',type=float,help="Scale factor, for example 0.5 to make tifs half scale")
    parser.add_argument('source_dir',type=readable_dir,help="Directory where source tif files are")
    parser.add_argument('target_dir',type=readable_dir)

    args = parser.parse_args()

    if args.rescale_factor <= 0:
        raise Exception("Rescale factor must be positive")

    tif_files = [filename for filename in os.listdir(args.source_dir) if filename.endswith(".tif")]
    tif_files.sort()

    for filename in tif_files:
        fp = os.path.join(args.source_dir,filename)

        img = imageio.imread(fp)

        dims = img.shape
        new_dims = []

        for dim in dims:
            new_dim = int(dim * args.rescale_factor)
            if new_dim == 0:
                raise Exception("Dimension {} in {} rescaled by factor {} becomes zero".format(dim,fp,args.rescale_factor))
            new_dims.append(new_dim)

        new_dims = tuple(new_dims)
        # cv2's resize keeps the image array in uint8 form
        print("Image shape: {}".format(str(img.shape)))
        print("Image type: {}".format(img.dtype))
        print("New dims: {}".format(str(new_dims)))
        resized_img = cv2.resize(img, dsize=new_dims)
        new_fp = os.path.join(args.target_dir, "resized_" + filename)

        imageio.imwrite(new_fp, resized_img)

