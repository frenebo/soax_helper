import argparse
import os

from .snakeutils.logger import ConsoleLogger
from .snakeutils.files import find_tiffs_in_dir

def get_num_of_tiff_fn(tiff_fn, tiff_name_prefix, postfix_length=0, logger=ConsoleLogger):
    fn_without_extension = os.path.splitext(tiff_fn)[0]
    if not fn_without_extension.startswith(tiff_name_prefix):
        logger.error("TIFF '{}' does not start with '{}', skipping".format(tiff_fn, tiff_name_prefix))
        return None

    if postfix_length != 0:
        tiff_num_str = fn_without_extension[len(tiff_name_prefix):-postfix_length]
    else:
        tiff_num_str = fn_without_extension[len(tiff_name_prefix):]

    try:
        tiff_num = int(tiff_num_str)
    except ValueError as e:
        logger.FAIL("Cannot parse string '{}' from '{}' as integer".format(tiff_num_str, tiff_fn))
    return tiff_num

def pad_tiff_numbers(
    tiff_dir,
    tiff_name_prefix,
    postfix_length=0,
    logger=ConsoleLogger,
):
    source_tiffs = find_tiffs_in_dir(tiff_dir)


    most_digits = 0
    for tiff_fn in source_tiffs:
        tiff_fn_num = get_num_of_tiff_fn(tiff_fn, tiff_name_prefix, postfix_length=postfix_length, logger=logger)
        if tiff_fn_num is None:
            continue
        num_digits = len(str(tiff_fn_num))
        if num_digits > most_digits:
            most_digits = num_digits

    # Rename files
    for tiff_fn in source_tiffs:
        tiff_fn_num = get_num_of_tiff_fn(tiff_fn, tiff_name_prefix, postfix_length=postfix_length, logger=logger)
        if tiff_fn_num is None:
            continue

        save_prefix = tiff_name_prefix
        if postfix_length != 0:
            save_postfix = os.path.splitext(tiff_fn)[0][-postfix_length:]
        else:
            save_postfix = ""


        new_tiff_fn = save_prefix + str(tiff_fn_num).zfill(most_digits) + save_postfix + ".tif"
        old_fp = os.path.join(tiff_dir, tiff_fn)
        new_fp = os.path.join(tiff_dir, new_tiff_fn)
        logger.log("Renaming {} to {}".format(tiff_fn, new_tiff_fn))
        os.rename(old_fp, new_fp)

