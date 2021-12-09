import os
from multiprocessing.pool import ThreadPool
import subprocess
import tqdm
from ctypes import c_int32
import time

from .snakeutils.logger import PrintLogger

def soax_instance(soax_instance_args):
    batch_soax = soax_instance_args["batch_soax"]
    tiff_dir = soax_instance_args["tiff_dir"]
    params_name = soax_instance_args["params_name"]
    param_fp = soax_instance_args["param_fp"]
    snakes_output_dir = soax_instance_args["snakes_output_dir"]
    delete_soax_logs_for_finished_runs = soax_instance_args["delete_soax_logs_for_finished_runs"]
    logger = soax_instance_args["logger"]
    stdout_fp = soax_instance_args["stdout_fp"]
    stderr_fp = soax_instance_args["stderr_fp"]

    success = None
    with open(stdout_fp,"w") as stdout_file, open(stderr_fp,"w") as error_file:
        command = "{batch_soax} --image {tiff_dir} --parameter {param_fp} --snake {snakes_output_dir}".format(
            batch_soax = batch_soax,
            tiff_dir=tiff_dir,
            param_fp=param_fp,
            snakes_output_dir=snakes_output_dir,
        )

        logger.log("Executing '{}'\n\t(Piping stdout to '{}' and stderr to '{}')".format(command, stdout_fp, stderr_fp))
        try:
            code = subprocess.run(command,shell=True,stdout=stdout_file,stderr=error_file,check=True).returncode
            logger.success("Completed {}".format(command))
            success = True
        except subprocess.CalledProcessError as e:
            logger.error("ERROR: ")
            logger.error("  Failed to run '{}' - return code {}".format(command,e.returncode))
            logger.error("    STDERR saved in {}".format(stderr_fp))
            logger.error("    STDOUT saved in {}".format(stdout_fp))
            success = False
    if success and delete_soax_logs_for_finished_runs:
        try:
            os.remove(stderr_fp)
            os.remove(stdout_fp)
        except:
            pass

def run_soax(
    batch_soax,
    tiff_dir,
    params_dir,
    output_dir,
    logging_dir,
    use_sectioned_images,
    use_image_specific_params,
    delete_soax_logs_for_finished_runs,
    workers_num,
    logger=PrintLogger):
    # # @TODO implemente image specific params
    # if

    # if len(param_files) == 0:
    #     logger.FAIL("No SOAX parameter files ending in .txt found in {}".format(params_dir))

    logger.log("WORKERS: {}".format(workers_num))

    soax_instance_args = []

    # If we have subdirectories for the sections of each images, we have
    # {tiff_dir} -> subdir0 -> tif,tif,tif,tif
    #                 subdir1 -> tif,tif,tif,tif,
    #                    ........
    #                 subdir123 -> tif,tif,tif,tif,
    # So we need to run soax on each subdir with each parameter
    if use_sectioned_images:
        tiff_dir_contents = os.listdir(tiff_dir)
        image_sections_dirnames = [name for name in tiff_dir_contents if os.path.isdir(os.path.join(tiff_dir,name))]
        image_sections_dirnames.sort()

        for image_sections_dirname in image_sections_dirnames:
            image_sections_dir_path = os.path.join(tiff_dir,image_sections_dirname)

            param_directory_for_this_image =

            if use_image_specific_params:
                params_dirpath_for_image = os.path.join(params_dir, image_sections_dirname)
            else:
                params_dirpath_for_image = params_dir

            param_files = [filename for filename in os.listdir(params_dirpath_for_image) if filename.endswith(".txt")]
            param_files.sort()

            if len(param_files) == 0:
                logger.FAIL("No SOAX parameter files ending in .txt found in {}".format(params_dirpath_for_image))

            for params_filename in param_files:
                param_fp = os.path.join(params_dirpath_for_image,params_filename)
                params_name = params_filename[:-len(".txt")]

                params_logging_dir = os.path.join(logging_dir, params_name)
                if not os.path.isdir(params_logging_dir):
                    if os.path.exists(params_logging_dir):
                        logger.FAIL("Logging dir {} exists but is not directory. Cannot log output there".format(sublogging_dir))
                    else:
                        os.makedirs(params_logging_dir)

                snakes_output_dir = os.path.join(output_dir, params_name, image_sections_dirname)

                stdout_fp = os.path.join(params_logging_dir, image_sections_dirname + "_stdout.txt")
                stderr_fp = os.path.join(params_logging_dir, image_sections_dirname + "_errors.txt")

                if not os.path.isdir(snakes_output_dir):
                    if os.path.exists(snakes_output_dir):
                        logger.FAIL("Snakes dir {} exists but is not a directory. Cannot output snakes here".format(snakes_output_dir))
                    else:
                        os.makedirs(snakes_output_dir)

                soax_instance_args.append({
                    "batch_soax": batch_soax,
                    "tiff_dir": image_sections_dir_path,
                    "param_fp": param_fp,
                    "params_name": params_name,
                    "snakes_output_dir": snakes_output_dir,
                    "delete_soax_logs_for_finished_runs": delete_soax_logs_for_finished_runs,
                    "stdout_fp": stdout_fp,
                    "stderr_fp": stderr_fp,
                    "logger": logger,
                })
    # If no sub directories for sections of images, we have
    # {tiff_dir} -> tif,tif,tif,tif
    # so we only need to run soax once with each param on the same directory
    else:
        if use_image_specific_params:
            raise Exception("It is not currently supported to use individual image parameters when the images are not sectioned")
        else:
            param_files = [filename for filename in os.listdir(params_dir) if filename.endswith(".txt")]
            param_files.sort()

        for params_filename in param_files:
            param_fp = os.path.join(params_dir,params_filename)
            params_name = params_filename[:-len(".txt")]


            snakes_output_dir = os.path.join(output_dir, params_name)
            if not os.path.isdir(snakes_output_dir):
                if os.path.exists(snakes_output_dir):
                    logger.FAIL("Snakes dir {} exists but is not a directory. Cannot output snakes here".format(snakes_output_dir))
                else:
                    os.makedirs(snakes_output_dir)

            soax_instance_args.append({
                "batch_soax": batch_soax,
                "tiff_dir": tiff_dir,
                "param_fp": param_fp,
                "params_name": params_name,
                "snakes_output_dir": snakes_output_dir,
                "delete_soax_logs_for_finished_runs": delete_soax_logs_for_finished_runs,
                "stdout_fp": os.path.join(logging_dir, params_name + "_stdout.txt"),
                "stderr_fp": os.path.join(logging_dir, params_name + "_errors.txt"),
                "logger": logger,
            })

    with ThreadPool(workers_num) as pool:
        future = pool.map(soax_instance, soax_instance_args, chunksize=1)
