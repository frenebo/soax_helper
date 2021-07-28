from snakeutils.files import readable_dir
import argparse
from PIL import Image
import numpy as np
import tifffile
import os
from snakeutils.logger import PrintLogger, Colors

def flatten_3d_tifs(source_dir,target_dir,logger=PrintLogger):

    tif_names = [name for name in os.listdir(source_dir) if name.endswith(".tif")]
    tif_names.sort()

    for src_tif_fn in tif_names:
        fp = os.path.join(source_dir,src_tif_fn)
        logger.log("Processing {}".format(fp))
        pil_img = Image.open(fp)

        # if just one frame
        if getattr(pil_img, "n_frames", 1) == 1:
            logger.error("Cannot flatten, TIF {} is already 2D".format(fp))
            return

        arr_3d = np.zeros((pil_img.height,pil_img.width,pil_img.n_frames),dtype=np.array(pil_img).dtype)

        for frame_idx in range(pil_img.n_frames):
            pil_img.seek(frame_idx)
            arr_3d[:,:, frame_idx] = np.array(pil_img)
        # Maximum intensity projection
        arr_2d = np.max(arr_3d,axis=2)

        new_tif_fn = "2d_" + src_tif_fn
        new_fp = os.path.join(target_dir, new_tif_fn)
        logger.success("  Saving flattened tif as {}".format(new_fp))

        tifffile.imsave(new_fp,arr_2d)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Maximum Intensity Projection to flatten 3D tifs to 2D tifs')
    parser.add_argument('source_dir',type=readable_dir,help="Directory where source 3Dtif files are")
    parser.add_argument('target_dir',type=readable_dir,help="Directory to save 2D flat tifs")

    args = parser.parse_args()

    flatten_3d_tifs(args.source_dir,args.target_dir)
