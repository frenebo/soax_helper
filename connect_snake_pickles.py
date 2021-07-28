import argparse
import os
import pickl
from snakeutils.logger import PrintLogger,Colors
from snakeutils.files import readable_dir

def get_is_3d_from_filename(fn):
    if fn.startswith("3Dsec"):
        return True
    elif fn.startswith("2Dsec"):
        return False
    else:
        return None

# Given image slice dimensions, finds the highest width height (and depth if 3D) indices in names
# and retuns the width height and depth the orig image must have had
def get_section_bounds(filenames, img_is_3d):
    # remove "xDsec_" and ".pickle"
    section_info = fn[6:-7]

    if img_is_3d:
        height_bounds,width_bounds,depth_bounds = section_info.split("_")
    else:
        height_bounds,width_bounds = section_info.split("_")

    sec_height_lower,sec_height_upper = height_bounds.split("-")
    sec_width_lower,sec_width_upper = width_bounds.split("-")
    if img_is_3d:
        sec_depth_lower,sec_depth_upper = depth_bounds.split("-")

    if img_is_3d:
        return sec_height_lower,sec_height_upper,sec_width_lower,sec_width_upper,sec_depth_lower,sec_depth_upper
    else:
        return sec_height_lower,sec_height_upper,sec_width_lower,sec_width_upper

def connect_snake_pickles(source_dir,target_dir,logger=PrintLogger):
    source_subdirs = [name for name in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir,name))]
    source_subdirs.sort()

    for source_subdir in source_subdirs:
        subdir_path = os.path.join(source_dir,source_subdir)
        snake_pickles = [name for name in os.listdir(subdir_path) if name.endswith(".pickle")]
        snake_pickles.sort()

        if len(snake_pickles) == 0:
            logger.log(" No .pickle files found in {}, aborting this directoy".format(subdir_path), Colors.RED)

        img_is_3d = get_is_3d_from_filename(snake_pickles[0])
        if img_is_3d is None:
            logger.log( " Expected pickle name '{}' to start '3Dsec' or '2Dsec'. Could not determine image dimensionality, aborting directory '{}'".format(snake_pickles[0],subdir_path), Colors.RED)
            continue

        dims_dont_match = False
        for section_fn in snake_pickles:
            if get_is_3d_from_filename(section_fn) != img_is_3d:
                logger.log(" Dimension in name '{}' does not match '{}', aborting this directory".format(section_fn,snake_pickles[0]), Colors.RED)
                dims_dont_match = True
                continue

        if dims_dont_match:
            continue

        shifted_snakes = {}
        for sec_idx,pickle_fn in enumerate(snake_pickles):
            section_bounds = get_section_bounds(pickle_fn,img_is_3d)
            if img_is_3d:
                sec_height_lower,sec_height_upper,sec_width_lower,sec_width_upper,sec_depth_lower,sec_depth_upper = section_bounds
            else:
                sec_height_lower,sec_height_upper,sec_width_lower,sec_width_upper = section_bounds

            with open(os.path.join(subdir_path,pickle_fn),'rb') as pickle_file:
                sec_snakes = pickle.load(pickle_file)

            for snake_name in sec_snakes.keys():
                shifted_snake_pts = []

                for unshifted_pt in sec_snakes[snake_name]:
                    if img_is_3d:
                        shifted_pt = [
                            unshifted_pt[0] + sec_width_lower,
                            unshifted_pt[1] + sec_height_lower,
                            unshifted_pt[2] + sec_depth_lower,
                        ]
                    else:
                        shifted_pt = [
                            unshifted_pt[0] + sec_width_lower,
                            unshifted_pt[1] + sec_height_lower,
                        ]
                    shifted_snake_pts.append(shifted_pt)
                new_snake_name = str(sec_idx) + "_" + snake_name
                shifted_snakes[new_snake_name] = shifted_snake_pts

        new_pickle_path = os.path.join(target_dir,source_subdir + ".pickle")
        with open(new_pickle_path,'wb') as handle:
            pickle.dump(shifted_snakes, handle, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('source_dir',type=readable_dir,help="Directory with snake pickles")
    parser.add_argument('target_dir',type=readable_dir,help="Directory to save pickled snakes")

    args = parser.parse_args()

    connect_snake_pickles(args.source_dir,args.target_dir)