from snakeutils.tifimage import save_3d_tif
import os
from PIL import Image
import numpy as np
import tifffile
from snakeutils.logger import PrintLogger

def subslice_tifs(start_slice, end_slice, source_dir,target_dir,logger=PrintLogger):
    new_n_frames = end_slice - start_slice + 1

    source_tifs = [filename for filename in os.listdir(source_dir) if filename.endswith(".tif")]

    for src_tiff_fn in souce_tifs:
        fp = os.path.join(source_dir,src_tiff_fn)
        logger.log("Processing {}".format(fp))

        pil_img = Image.open(fp)

        img_is_3d = getattr(pil_img, "n_frames", 1) != 1

        if not img_is_3d:
            logger.FAIL("Cannot slice {}, is not a 3D tif file".format(fp))

        if pil_img.n_frames < end_slice + 1:
            logger.FAIL("Can't take slices {}-{}, tif only has {} frames".format(start_slice,end_slice,pil_img.n_frames))

        new_img_arr = np.zeros((pil_img.height,pil_img.width,new_n_frames),dtype=np.array(pil_img).dtype)

        logger.log("Extracting slices {}-{} from depth {} image".format(start_slice,end_slice,pil_img.n_frames))
        for frame_idx in range(start_slice,end_slice + 1):
            pil_img.seek(frame_idx)
            new_img_arr[:,:, frame_idx - start_slice] = np.array(pil_img)

        new_tiff_fn = "{}-{}sliced_".format(start_slice,end_slice) + src_tiff_fn
        new_fp = os.path.join(target_dir, new_tiff_fn)
        logger.log("Saving sliced image as {}".format(new_fp))

        save_3d_tif(new_fp, new_img_arr)
