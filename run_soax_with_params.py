import argparse
from snakeutils.files import readable_dir
import os
import multiprocessing as mp
from multiprocessing.pool import ThreadPool
import subprocess
import tqdm
from ctypes import c_int32
import time
from colorama import init, Fore, Back,Style
init()

# print(Fore.RED + 'some red text')
# print(Back.GREEN + 'and with a green background')
# #print(Style.DIM + 'and in dim text')
# print(Style.RESET_ALL)
# print('back to normal now')

def run_soax(soax_args):
    batch_soax = soax_args["batch_soax"]
    tif_dir = soax_args["tif_dir"]
    params_name = soax_args["params_name"]
    param_fp = soax_args["param_fp"]
    params_output_dir = soax_args["params_output_dir"]
    logging_dir = soax_args["logging_dir"]

    error_fp = os.path.join(logging_dir,"error_" + params_name + ".txt")

    stdout_fp = os.path.join(logging_dir,"stdout_" + params_name + ".txt")

    with open(error_fp,"w") as error_file, open(stdout_fp,"w") as stdout_file:
        command = "{batch_soax} --image {tif_dir} --parameter {param_fp} --snake {params_output_dir}".format(
            batch_soax = batch_soax,
            tif_dir=tif_dir,
            param_fp=param_fp,
            params_output_dir=params_output_dir,
        )

        print("Executing '{}'".format(command))
        try:
            code = subprocess.run(command,shell=True,stdout=stdout_file,stderr=error_file,check=True).returncode
            print(Fore.GREEN + "Completed {}".format(command) + Style.RESET_ALL)
        except subprocess.CalledProcessError as e:
            print(Fore.RED + "ERROR: ")
            print("Failed to run {}. return code {}".format(command,e.returncode))
            print(Style.RESET_ALL)


def generate_run_soax_args(params_dir,params_filename,output_dir,batch_soax,tif_dir,logging_dir):
    param_fp = os.path.join(params_dir,params_filename)
    params_name = params_filename[:-len(".txt")]
    params_output_dir = os.path.join(output_dir,params_name)

    return {
        "batch_soax": batch_soax,
        "tif_dir": tif_dir,
        "param_fp": param_fp,
        "params_name": params_name,
        "params_output_dir": params_output_dir,
        "logging_dir":logging_dir,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('batch_soax',help="Path to batch_soax executable")
    parser.add_argument('tif_dir',type=readable_dir,help='Directory with tif files to run in soax')
    parser.add_argument('params_dir',type=readable_dir,help='Directory with soax param text files')
    parser.add_argument('output_dir',type=readable_dir,help='Directory to put')
    parser.add_argument('logging_dir', type=readable_dir,help='Directory to write error messages')
    parser.add_argument('--subdirs', default=False, action='store_true',help='If tif_dir has subdirectories of image')
    parser.add_argument('--workers', default=5, type=int, help='Number of batch_soax processes to have running at once')

    args = parser.parse_args()
    param_files = [filename for filename in os.listdir(args.params_dir) if filename.endswith(".txt")]
    param_files.sort()

    workers_num = args.workers
    print("WORKERS: {}".format(workers_num))

    soax_args = []

    # If recursive subdirs, we have
    # args.tif_dir -> subdir0 -> tif,tif,tif,tif
    #                 subdir1 -> tif,tif,tif,tif,
    #                    ........
    #                 subdir123 -> tif,tif,tif,tif,
    # So we need to run soax on each subdir with parameter
    if args.subdirs:
        tif_dir_contents = os.listdir(args.tif_dir)
        subdir_names = [name for name in tif_dir_contents if os.path.isdir(os.path.join(args.tif_dir,name))]
        subdir_names.sort()

        for subdir_name in subdir_names:
            subdir_path = os.path.join(args.tif_dir,subdir_name)
            output_subdir_path = os.path.join(args.output_dir,subdir_name)
            sublogging_dir = os.path.join(args.logging_dir,subdir_name)
            os.mkdir(sublogging_dir)
            if os.path.exists(output_subdir_path):
                raise Exception("Target dir {} already exists".format(output_subdir_path))
            os.mkdir(output_subdir_path)

            for params_filename in param_files:
                soax_args.append(generate_run_soax_args(
                    args.params_dir,
                    params_filename,
                    output_subdir_path,
                    args.batch_soax,
                    subdir_path,
                    sublogging_dir,
                ))
    # If no subdirs, we have
    # args.tif_dir -> tif,tif,tif,tif
    # so we only need to run soax once with each param on the same directory
    else:
        for params_filename in param_files:
            soax_args.append(generate_run_soax_args(
                args.params_dir,
                params_filename,
                args.output_dir,
                args.batch_soax,
                args.tif_dir,
                args.logging_dir
            ))

    print("Creating snake output directories inside {}".format(args.output_dir))
    for soax_arg in soax_args:
        params_output_dir = soax_arg["params_output_dir"]
        os.mkdir(params_output_dir)
        print("Directory '{}' created".format(params_output_dir))

    with ThreadPool(workers_num) as pool:
        print("Making future")
        future = pool.map(run_soax, soax_args)
        print("Future finished")


