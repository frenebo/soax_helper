import argparse
from snakeutils.logger import PrintLogger
import os
from snakeutils.files import has_one_of_extensions

def get_num_of_tiff_fn(tiff_fn, tiff_name_prefix, logger):
    fn_without_extension = os.path.splitext(tiff_fn)[0]
    if not fn_without_extension.startswith(tiff_name_prefix):
        logger.error("Tif '{}' does not start with '{}', skipping".format(tiff_fn, tiff_name_prefix))
        return None
    tiff_num_str = fn_without_extension[len(tiff_name_prefix):]
    try:
        tiff_num = int(tiff_num_str)
    except ValueError as e:
        logger.FAIL("Cannot parse string '{}' from '{}' as integer".format(tiff_num_str, tiff_fn))
    return tiff_num

def pad_tiff_numbers(
    tiff_dir,
    tiff_name_prefix,
    logger=PrintLogger,
):
    source_tifs = [filename for filename in os.listdir(tiff_dir) if has_one_of_extensions(filename, [".tif", ".tiff"])]
    source_tifs.sort()

    most_digits = 0
    for tiff_fn in source_tifs:
        tiff_fn_num = get_num_of_tiff_fn(tiff_fn, tiff_name_prefix, logger)
        if tiff_fn_num is None:
            continue
        num_digits = len(str(tiff_fn_num))
        if num_digits > most_digits:
            most_digits = num_digits

    # Rename files
    for tiff_fn in source_tifs:
        tiff_fn_num = get_num_of_tiff_fn(tiff_fn, tiff_name_prefix, logger)
        if tiff_fn_num is None:
            continue

        new_tiff_fn = tiff_name_prefix + str(tiff_fn_num).zfill(most_digits) + ".tifs"
        old_fp = os.path.join(tiff_dir, tiff_fn)
        new_fp = os.path.join(tiff_dir, new_tiff_fn)
        logger.log("Renaming {} to {}".format(tiff_fn, new_tiff_fn))
        os.rename(old_fp, new_fp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pad numbers of of tif filenames in directory')
    parser.add_argument("tiff_dir")
    parser.add_argument("tiff_name_prefix")

    args = parser.parse_args()

    pad_tiff_numbers(args.tiff_dir, args.tiff_name_prefix)
