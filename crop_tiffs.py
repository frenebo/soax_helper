import argparse
from snakeutils.logger import PrintLogger

def crop_tiffs(
    source_tiff_dir,
    min_x,
    max_x,
    min_y,
    max_y,
    min_z,
    max_z,
    logger=PrintLogger,
):
    source_tiffs = [filename for filename in os.listdir(source_dir) if has_one_of_extensions(filename, [".tif", ".tiff"])]
    source_tiffs.sort()

    for tif_name in source_tiffs:

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crop tiffs from source directory and save in target directory')
    parser.add_argument("source_dir")
    parser.add_argument("target_dir")
    parser.add_argument("min_x", type=int)
    parser.add_argument("max_x", type=int)
    parser.add_argument("min_y", type=int)
    parser.add_argument("max_y", type=int)
    parser.add_argument("min_z", type=int)
    parser.add_argument("max_z", type=int)

    args = parser.parse_args()


