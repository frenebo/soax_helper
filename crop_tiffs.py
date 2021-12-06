import argparse

def crop_tiffs(
    source_tiff_dir,
    target_tiff_dir,
):
    raise NotImplementedError()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crop tiffs from source directory and save in target directory')
    parser.add_argument("source_dir")
    parser.add_argument("target_dir")

    args = parser.parse_args()


