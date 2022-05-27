import argparse
import os
from PIL import Image

from snakeutils.tifimage import open_tiff_as_np_arr, save_3d_tif
from snakeutils.files import find_tiffs_in_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Split 3D Tiff into its 2D frames')
    parser.add_argument('source_tiff_dir')
    parser.add_argument('target_directory')
    parser.add_argument('start_t',type=int)
    parser.add_argument('t_length',type=int)
    parser.add_argument('start_z',type=int)
    parser.add_argument('z_length',type=int)

    args = parser.parse_args()

    if not os.path.exists(args.target_directory):
        os.makedirs(args.target_directory)
    else:
        if not os.path.isdir(args.target_directory):
            raise Exception("Bad target directory '{}': should be a directory to put the TIFF frames into".format(args.target_directory))

    orig_tiffs = find_tiffs_in_dir(args.source_tiff_dir)

    # fulltiff_names = []
    fulltiffs_by_t_and_z = {}

    for orig_tiff_fn in orig_tiffs:
        tiff_path = os.path.join(args.source_tiff_dir, orig_tiff_fn)
        # image_name_without_extension = os.path.splitext(orig_tiff_fn)[0]

        tiff_tstr = orig_tiff_fn[args.start_t:args.start_t+args.t_length]
        tiff_zstr = orig_tiff_fn[args.start_z:args.start_z+args.z_length]
        tiff_t = int(tiff_tstr)
        tiff_z = int(tiff_zstr)

        # fulltiffs_by_t_and_z
        if tiff_t not in fulltiffs_by_t_and_z:
            fulltiffs_by_t_and_z[tiff_t] = {}

        if tiff_z in fulltiffs_by_t_and_z[tiff_t]:
            raise Exception("Already have a tiff with t={},z={} - conflict between {} and {}".format(
                tiff_t,
                tiff_z,
                fulltiffs_by_t_and_z[tiff_t][tiff_z],
                orig_tiff_fn,
            ))

        fulltiffs_by_t_and_z[tiff_t][tiff_z] = tiff_path

    zsize = len(fulltiffs_by_t_and_z[min(fulltiffs_by_t_and_z.keys())])
    for timeidx in fulltiffs_by_t_and_z:
        zdict = fulltiffs_by_t_and_z[timeidx]
        if len(zdict) != zsize:
            raise Exception("Had {} z stacks for t={}, not same as first image, which has {} zstacks".format(
                len(zdict),timeidx,zsize
            ))
        stack_zmin = min(zdict.keys())
        stack_zmax = max(zdict.keys())
        if stack_zmax - stack_zmin != zsize - 1:
            raise Exception("Missing zstacks for t={}".format(timeidx))

    for timeidx in fulltiffs_by_t_and_z:
        print("Constructing tiff for t={}".format(timeidx))
        zdict = fulltiffs_by_t_and_z[timeidx]
        zmin = min(zdict.keys())
        zmax = max(zdict.keys())

        first_tiff_arr = open_tiff_as_np_arr(zdict[zmin])
        if len(first_tiff_arr.shape != 2):
            raise Exception("Stack is not 2d: {}".format(zdict[zmin]))
        full_arr = np.zeros(first_tiff_arr.shape + (zsize,), dtype=first_tiff_arr.dtype )


        for zidx in range(zsize):
            zslice_arr = open_tiff_as_np_arr(zdict[zmin+zidx])
            if len(zslice_arr.shape != 2):
                raise Exception("Stack is not 2d: {}".format(zdict[zmin+zidx]))
            full_arr[:,:,zidx] = zslice_arr

        save_tiff_path = os.path.join(args.target_directory, "T"+str(timeidx))
        save_3d_tif(save_tiff_path, full_arr)



    # image_params_dirpath = os.path.join(params_save_dir, image_name_without_extension)
    # os.mkdir(image_params_dirpath)
    # 1x1_40x_photometrics_1sInt_2umZstep_MTsAndBeads_May23_

    # np_arr = open_tiff_as_np_arr(args.source_tiff_path)

    # print("shape: {}".format(np_arr.shape))

    # tiff_name = os.path.split(args.source_tiff_path)[-1]

    # stack_num = np_arr.shape[2]
    # # "_{filename_tag}{{{name}:0{str_length}.{decimals}f}}"
    # prefix_template = "{{idx:0{str_length}.0f}}_".format(str_length=len(str(stack_num - 1)))
    # for i in range(stack_num):
    #     fp = os.path.join(args.target_directory, prefix_template.format(idx=i) + tiff_name)
    #     save_3d_tif(fp, np_arr[:,:,i:i+1])
    #     print("Saved {}".format(fp))