import os
from multiprocessing.pool import ThreadPool
import subprocess
import tqdm
from ctypes import c_int32
import time

from .snakeutils.files import find_files_or_folders_at_depth

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

def args_to_run_soax_on_image_dir_with_dir_of_paramfiles(
    batch_soax,
    tiff_dir,
    param_file_dir,
    snakes_dir,
    logging_dir,
    delete_soax_logs_for_finished_runs,
    logger,
):
    if not os.path.isdir(snakes_dir):
        if os.path.exists(snakes_dir):
            logger.FAIL("Output snakes dir {} exists but is not directory. Cannot output snakes there".format(snakes_dir))
        else:
            os.makedirs(snakes_dir)

    if not os.path.isdir(logging_dir):
        if os.path.exists(logging_dir):
            logger.FAIL("Logging dir {} exists but is not directory. Cannot log output there".format(logging_dir))
        else:
            os.makedirs(logging_dir)

    arg_dicts = []

    param_files = [filename for filename in os.listdir(param_file_dir) if filename.endswith(".txt")]
    param_files.sort()

    for param_filename in param_files:
        param_fp = os.path.join(param_file_dir, param_filename)
        params_name = os.path.splitext(param_filename)[0]

        logging_dir_for_params = os.path.join(logging_dir, params_name)
        if not os.path.isdir(logging_dir_for_params):
            if os.path.exists(logging_dir_for_params):
                logger.FAIL("Logging dir {} exists but is not directory. Cannot log output there".format(logging_dir_for_params))
            else:
                os.makedirs(logging_dir_for_params)

        stdout_fp = os.path.join(logging_dir_for_params, "stdout.txt")
        stderr_fp = os.path.join(logging_dir_for_params, "stderr.txt")

        arg_dicts.append({
            "batch_soax": batch_soax,
            "tiff_dir":  tiff_dir,
            "param_fp": param_fp,
            "params_name":  params_name,
            "snakes_output_dir": snakes_dir,
            "delete_soax_logs_for_finished_runs": delete_soax_logs_for_finished_runs,
            "stdout_fp": stdout_fp,
            "stderr_fp": stderr_fp,
            "logger": logger,
        })

    return arg_dicts

def run_soax(
    batch_soax,
    base_image_dir,
    base_params_dir,
    base_output_dir,
    base_logging_dir,
    use_sectioned_images,
    use_image_specific_params,
    delete_soax_logs_for_finished_runs,
    workers_num,
    logger,
):
    logger.log("Running SOAX with {} batch_soax worker instances".format(workers_num))

    soax_instance_arg_dicts  = []


    if use_image_specific_params and not use_sectioned_images:
        logger.FAIL("Currently it isn't supported to use image-specific parameters without sectioned images")

    if use_sectioned_images:
        image_dirs_depth = 1
    else:
        image_dirs_depth = 0

    input_image_dirs_info = find_files_or_folders_at_depth(base_image_dir, image_dirs_depth, folders_not_files=True)


    if use_sectioned_images:
        image_dirs_info = find_files_or_folders_at_depth(base_image_dir, 0, folders_not_files=True)
        image_dirnames = [dirname for containing_path, dirname in image_dirs_info]

        # check there's a param directory for each image
        if use_image_specific_params:
            param_dirs_info = find_files_or_folders_at_depth(base_params_dir, 0, folders_not_files=True)
            param_dirnames = [dirname for containing_path, dirname in param_dirs_info]

            if len(image_dirnames) != len(param_dirnames):
                logger.FAIL(("Expected same number of image section directories as param directories, "
                    "but found {} image directories in {} and {} param directories in {}").format(
                        len(image_dirnames), base_image_dir, len(param_dirnames), base_params_dir,
                ))
            for img_idx in range(len(image_dirnames)):
                image_dirname = image_dirnames[img_idx]
                param_dirname = param_dirnames[img_idx]

                if image_dirname != param_dirname:
                    logger.FAIL(("Expected to have matching image dirs and param dirs, but "
                        "name of an image dir '{}' doesn't match with the name of a param dir '{}'").format(
                            image_dirname, param_dirname
                    ))

        for img_idx, image_dirname in enumerate(image_dirnames):
            image_dirpath = os.path.join(base_image_dir, image_dirname)
            if use_image_specific_params:
                param_dir = os.path.join(base_params_dir, param_dirnames[img_idx])
            else:
                param_dir = base_params_dir

            snakes_dir = os.path.join(base_output_dir, image_dirname)
            logging_dir = os.path.join(base_logging_dir, image_dirname)

            soax_instance_arg_dicts += args_to_run_soax_on_image_dir_with_dir_of_paramfiles(
                batch_soax,
                image_dirpath,
                param_dir,
                snakes_dir,
                logging_dir,
                delete_soax_logs_for_finished_runs,
                logger,
            )
    # Not using sectioned images
    else:
        if use_image_specific_params:
            logger.FAIL("Currently it isn't supported to use image-specific parameters without sectioned images")

        soax_instance_arg_dicts += args_to_run_soax_on_image_dir_with_dir_of_paramfiles(
            batch_soax,
            base_image_dir,
            base_params_dir,
            base_output_dir,
            base_logging_dir,
            delete_soax_logs_for_finished_runs,
            logger,
        )

    with ThreadPool(workers_num) as pool:
        future = pool.map(soax_instance, soax_instance_arg_dicts, chunksize=1)
