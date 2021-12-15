import os
import argparse
from PIL import Image
from multiprocessing.pool import ThreadPool

from .snakeutils.logger import PrintLogger
from .snakeutils.tifimage import save_3d_tif, pil_img_3d_to_np_arr
from .snakeutils.files import find_tiffs_in_dir

def crop_tiff(
    arg_dict,
):
    source_tiff_fp = arg_dict["source_tiff_fp"]
    target_tiff_fp = arg_dict["target_tiff_fp"]
    start_x = arg_dict["start_x"]
    end_x = arg_dict["end_x"]
    start_y = arg_dict["start_y"]
    end_y = arg_dict["end_y"]
    start_z = arg_dict["start_z"]
    end_z = arg_dict["end_z"]
    logger = arg_dict["logger"]

    logger.log("Loading tiff {} to crop".format(source_tiff_fp))
    pil_img = Image.open(source_tiff_fp)
    img_arr = pil_img_3d_to_np_arr(pil_img)
    cropped_img_arr = img_arr[
        start_y:end_y,
        start_x:end_x,
        start_z:end_z,
    ]
    logger.success("    Saving cropped tiff to {}".format(target_tiff_fp))
    save_3d_tif(target_tiff_fp,cropped_img_arr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crop tiffs from source directory and save in target directory')
    parser.add_argument("source_dir")
    parser.add_argument("target_dir")
    parser.add_argument("start_x", type=int)
    parser.add_argument("end_x", type=int)
    parser.add_argument("start_y", type=int)
    parser.add_argument("end_y", type=int)
    parser.add_argument("start_z", type=int)
    parser.add_argument("end_z", type=int)
    parser.add_argument("--workers", default=1, type=int)

    args = parser.parse_args()

    source_tiffs = find_tiffs_in_dir(args.source_dir)

    crop_tiffs_arg_dicts = []
    for tif_name in source_tiffs:
        source_tiff_fp = os.path.join(args.source_dir, tif_name)
        target_tiff_fp = os.path.join(args.target_dir, tif_name)

        arg_dict = {
            "source_tiff_fp": source_tiff_fp,
            "target_tiff_fp": target_tiff_fp,
            "start_x": args.start_x,
            "end_x": args.end_x,
            "start_y": args.start_y,
            "end_y": args.end_y,
            "start_z": args.start_z,
            "end_z": args.end_z,
            "logger": PrintLogger,
        }
        crop_tiffs_arg_dicts.append(arg_dict)

    with ThreadPool(args.workers) as pool:
        future = pool.map(crop_tiff, crop_tiffs_arg_dicts, chunksize=1)
