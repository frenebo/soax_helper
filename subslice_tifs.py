from snakeutils.files import readable_dir
import os
import argparse

def slice_range(arg_str):
    split_by_dash = arg.split('-')

    if len(split_by_dash) != 2:
        raise argparse.ArgumentTypeError("Argument {} should have start and end slice index separated by one dash. Ex: '10-13'".format(arg_str))

    try:
        start = int(split_by_dash[0])
    except ValueError as e:
        raise argparse.ArgumentTypeError("Couldn't parse {} as integer in range {}: {}".format(split_by_dash[0],arg_str,str(e)))

    try:
        end = int(split_by_dash[1])
    except ValueError as e:
        raise argparse.ArgumentTypeError("Couldn't parse {} as integer in range {}: {}".format(split_by_dash[1],arg_str,str(e)))

    if end < start:
        raise argparse.ArgumentTypeError("Start slice index {} is greater than end {}".format(start,end))

    return start,end



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('slice_range',type=slice_range,help="Range of TIF slices to keep. Ex 10-20 to keep slices 10-20, inclusive")
    parser.add_argument('source_dir',type=readable_dir,help="Directory where source tif files are")
    parser.add_argument('target_dir',type=readable_dir,help="Directory to save subslice tifs")

    args = parser.parse_args()

    for src_tif_fn in args.source_dir:
        print(src_tif_fn)