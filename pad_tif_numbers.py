import argparse
from snakeutils.logger import PrintLogger
import os
from snakeutils.files import has_one_of_extensions

def get_num_of_tif_fn(tiff_fn, tiff_name_prefix, logger):
    fn_without_extension = os.path.splitext(tif_fn)[0]
    if not fn_without_extension.startswith(tiff_name_prefix):
        logger.error("Tif '{}' does not start with '{}', skipping".format(tif_fn, tiff_name_prefix))
        return None
    tif_num_str = fn_without_extension[len(tiff_name_prefix):]
    try:
        tif_num = int(tif_num_str)
    except ValueError as e:
        logger.FAIL("Cannot parse string '{}' from '{}' as integer".format(tif_num_str, tif_fn))
    return tif_num

def pad_tif_numbers(
    tiff_dir,
    tiff_name_prefix,
    logger=PrintLogger,
):
    source_tifs = [filename for filename in os.listdir(tiff_dir) if has_one_of_extensions(filename, [".tif", ".tiff"])]
    source_tifs.sort()

    most_digits = 0
    for tif_fn in source_tifs:
        tif_fn_num = get_num_of_tif_fn(tiff_fn, tiff_name_prefix, logger)
        if tif_fn_num is None:
            continue
        num_digits = len(str(tif_fn_num))
        if num_digits > most_digits:
            most_digits = num_digits

    # Rename files
    for tif_fn in source_tifs:
        tif_fn_num = get_num_of_tif_fn(tiff_fn, tiff_name_prefix, logger)
        if tif_fn_num is None:
            continue

        new_tiff_fn = tiff_name_prefix + str(tif_fn_num).zfill(most_digits) + ".tifs"
        old_fp = os.path.join(tiff_dir, tif_fn)
        new_fp = os.path.join(tiff_dir, new_tiff_fn)
        logger.log("Renaming {} to {}".format(tif_fn, new_tiff_fn))
        os.rename(old_fp, new_fp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pad numbers of of tif filenames in directory')
    parser.add_argument("tiff_dir")
    parser.add_argument("tiff_name_prefix")

    args = parser.parse_args()

    pad_tif_numbers(args.tiff_dir, args.tiff_name_prefix)
