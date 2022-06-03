import argparse
import os

from .snakeutils.logger import ConsoleLogger
from .snakeutils.files import find_tiffs_in_dir

def get_num_of_tiff_fn(tiff_fn, tiff_name_prefix, logger):
    fn_without_extension = os.path.splitext(tiff_fn)[0]
    if not fn_without_extension.startswith(tiff_name_prefix):
        logger.error("TIFF '{}' does not start with '{}', skipping".format(tiff_fn, tiff_name_prefix))
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
    replace_prefix=None,
    logger=ConsoleLogger,
):
    source_tiffs = find_tiffs_in_dir(tiff_dir)

    if replace_prefix is not None:
        save_prefix = replace_prefix
    else:
        save_prefix = tiff_name_prefix

    most_digits = 0
    for tiff_fn in source_tiffs:
        tiff_fn_num = get_num_of_tiff_fn(tiff_fn, tiff_name_prefix, logger)
        if tiff_fn_num is None:
            continue
        num_digits = len(str(tiff_fn_num))
        if num_digits > most_digits:
            most_digits = num_digits

    # Rename files
    for tiff_fn in source_tiffs:
        tiff_fn_num = get_num_of_tiff_fn(tiff_fn, tiff_name_prefix, logger)
        if tiff_fn_num is None:
            continue



        new_tiff_fn = save_prefix + str(tiff_fn_num).zfill(most_digits) + ".tif"
        old_fp = os.path.join(tiff_dir, tiff_fn)
        new_fp = os.path.join(tiff_dir, new_tiff_fn)
        logger.log("Renaming {} to {}".format(tiff_fn, new_tiff_fn))
        os.rename(old_fp, new_fp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pad numbers of of TIFF filenames in directory')
    parser.add_argument("tiff_dir")
    parser.add_argument("tiff_name_prefix")
    parser.add_argument('--replaceprefix', default=None)

    args = parser.parse_args()

    pad_tiff_numbers(args.tiff_dir, args.tiff_name_prefix, replace_prefix=args.replaceprefix, logger=ConsoleLogger())
