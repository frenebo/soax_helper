import argparse
from snakeutils.files import readable_dir
import os
import multiprocessing as mp
from multiprocessing.pool import ThreadPool
import subprocess
import tqdm
from ctypes import c_int32
import time
from snakeutils.logger import PrintLogger, Colors

def run_soax(soax_args):
    batch_soax = soax_args["batch_soax"]
    tif_dir = soax_args["tif_dir"]
    params_name = soax_args["params_name"]
    param_fp = soax_args["param_fp"]
    params_output_dir = soax_args["params_output_dir"]
    logging_dir = soax_args["logging_dir"]
    logger = soax_args["logger"]

    error_fp = os.path.join(logging_dir,"error_" + params_name + ".txt")

    stdout_fp = os.path.join(logging_dir,"stdout_" + params_name + ".txt")

    with open(error_fp,"w") as error_file, open(stdout_fp,"w") as stdout_file:
        command = "{batch_soax} --image {tif_dir} --parameter {param_fp} --snake {params_output_dir}".format(
            batch_soax = batch_soax,
            tif_dir=tif_dir,
            param_fp=param_fp,
            params_output_dir=params_output_dir,
        )

        logger.log("Executing '{}'".format(command))
        try:
            code = subprocess.run(command,shell=True,stdout=stdout_file,stderr=error_file,check=True).returncode
            logger.log("Completed {}".format(command), Colors.GREEN)
        except subprocess.CalledProcessError as e:
            logger.log("ERROR: ", Colors.RED)
            logger.log("Failed to run {}. return code {}".format(command,e.returncode), Colors.RED)
            logger.log("STDERR saved in {}".format(error_fp), Colors.RED)
            logger.log("STDOUT saved in {}".format(stdout_fp), Colors.RED)


def generate_run_soax_args(params_dir,params_filename,output_dir,batch_soax,tif_dir,logging_dir,logger):
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
        "logger": logger,
    }

def run_soax_with_params(
    batch_soax,
    tif_dir,
    params_dir,
    output_dir,
    logging_dir,
    use_subdirs,
    workers_num,
    logger=PrintLogger):
    param_files = [filename for filename in os.listdir(params_dir) if filename.endswith(".txt")]
    param_files.sort()

    logger.log("WORKERS: {}".format(workers_num))

    soax_args = []

    # If recursive subdirs, we have
    # {tif_dir} -> subdir0 -> tif,tif,tif,tif
    #                 subdir1 -> tif,tif,tif,tif,
    #                    ........
    #                 subdir123 -> tif,tif,tif,tif,
    # So we need to run soax on each subdir with parameter
    if use_subdirs:
        tif_dir_contents = os.listdir(tif_dir)
        subdir_names = [name for name in tif_dir_contents if os.path.isdir(os.path.join(tif_dir,name))]
        subdir_names.sort()

        for subdir_name in subdir_names:
            subdir_path = os.path.join(tif_dir,subdir_name)
            output_subdir_path = os.path.join(output_dir,subdir_name)
            sublogging_dir = os.path.join(logging_dir,subdir_name)
            os.mkdir(sublogging_dir)
            if os.path.exists(output_subdir_path):
                raise Exception("Target dir {} already exists".format(output_subdir_path))
            os.mkdir(output_subdir_path)

            for params_filename in param_files:
                soax_args.append(generate_run_soax_args(
                    params_dir,
                    params_filename,
                    output_subdir_path,
                    batch_soax,
                    subdir_path,
                    sublogging_dir,
                    logger,
                ))
    # If no subdirs, we have
    # {tif_dir} -> tif,tif,tif,tif
    # so we only need to run soax once with each param on the same directory
    else:
        for params_filename in param_files:
            soax_args.append(generate_run_soax_args(
                params_dir,
                params_filename,
                output_dir,
                batch_soax,
                tif_dir,
                logging_dir
            ))

    logger.log("Creating snake output directories inside {}".format(output_dir))
    for soax_arg in soax_args:
        params_output_dir = soax_arg["params_output_dir"]
        os.mkdir(params_output_dir)
        logger.log("Directory '{}' created".format(params_output_dir))

    with ThreadPool(workers_num) as pool:
        logger.log("Making future")
        future = pool.map(run_soax, soax_args)
        logger.log("Future finished")


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

    run_soax_with_params(
        args.batch_soax,
        args.tif_dir,
        args.params_dir,
        args.output_dir,
        args.logging_dir,
        args.subdirs,
        args.workers_num,
    )

