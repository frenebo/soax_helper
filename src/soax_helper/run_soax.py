import os
from multiprocessing.pool import ThreadPool
import subprocess
import tqdm
from ctypes import c_int32
import time

from .snakeutils.files import find_files_or_folders_at_depth, find_tiffs_in_dir, has_one_of_extensions

def soax_instance(soax_instance_args):
    batch_soax_path = soax_instance_args["batch_soax_path"]
    tiff_fp = soax_instance_args["tiff_fp"]
    params_fp = soax_instance_args["params_fp"]
    snakes_output_dir = soax_instance_args["snakes_output_dir"]
    logging_dir = soax_instance_args["logging_dir"]
    delete_soax_logs_for_finished_runs = soax_instance_args["delete_soax_logs_for_finished_runs"]
    logger = soax_instance_args["logger"]

    stdout_fp = os.path.join(logging_dir, "stdout.txt")
    stderr_fp = os.path.join(logging_dir, "stderr.txt")

    success = None
    with open(stdout_fp,"w") as stdout_file, open(stderr_fp,"w") as error_file:
        command = "{batch_soax_path} --image {tiff_fp} --parameter {params_fp} --snake {snakes_output_dir}".format(
            batch_soax_path = batch_soax_path,
            tiff_fp=tiff_fp,
            params_fp=params_fp,
            snakes_output_dir=snakes_output_dir,
        )

        logger.log("Executing '{}'\n    (stdout in '{}' and stderr in '{}')".format(command, stdout_fp, stderr_fp))
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

def soax_args_for_tiff_and_param_file(
    batch_soax_path,
    tiff_fp,
    params_fp,
    snakes_dir,
    logging_dir,
    delete_soax_logs_for_finished_runs,
    logger,
):
    return {
        "batch_soax_path": batch_soax_path,
        "tiff_fp":  tiff_fp,
        "params_fp":  params_fp,
        "snakes_output_dir": snakes_dir,
        "logging_dir": logging_dir,
        "delete_soax_logs_for_finished_runs": delete_soax_logs_for_finished_runs,
        "logger": logger,
    }

def find_param_files_in_dir(dirpath):
    param_file_names = [filename for filename in os.listdir(dirpath) if has_one_of_extensions(filename, [".txt"])]
    param_file_names.sort()
    return param_file_names

def make_dir_if_not_exist(dirpath, logger):
    if not os.path.isdir(dirpath):
        if os.path.exists(dirpath):
            logger.FAIL("Failed to create directory {}, that location exists already but is not a directory".format(dirpath))
        else:
            os.makedirs(dirpath)

def run_soax(
    batch_soax_path,
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
    soax_instance_arg_dicts = []

    if use_image_specific_params:
        param_dirs_info = find_files_or_folders_at_depth(base_params_dir, 0, folders_not_files=True)
        param_dirnames = [dirname for containing_path, dirname in param_dirs_info]

        if not use_sectioned_images:
            tiff_filenames = find_tiffs_in_dir(base_image_dir)

            # Check that there is exactly one param dir for each tiff
            if len(param_dirnames) != len(tiff_filenames):
                logger.FAIL(("Expected same number of images as param directories, "
                    "but found {} images in {} and {} param directories in {}").format(
                        len(tiff_filenames), base_image_dir,len(param_dirnames), base_params_dir,
                ))

            # Match image files and param directories together
            for image_num, (param_dirname_for_tiff, tiff_fn) in enumerate(zip(param_dirnames, tiff_filenames), start=1):
                image_name_extensionless = os.path.splitext(tiff_fn)[0]
                # Check that image name matches with param dir name
                if image_name_extensionless != param_dirname_for_tiff:
                    logger.FAIL(("Parameter folder names in {} and image names in {} don't match: "
                        "At image # {}, {} doesn't match with {}").format(
                            base_params_dir, base_image_dir,
                            image_num, param_dirname_for_tiff, tiff_fn
                        ))
                image_path = os.path.join(base_image_dir, tiff_fn)
                param_folder_path_for_tiff = os.path.join(base_params_dir, param_dirname_for_tiff)

                param_filenames = find_param_files_in_dir(param_folder_path_for_tiff)

                for param_filename in param_filenames:
                    param_name_extensionless = os.path.splitext(param_filename)[0]
                    param_filepath = os.path.join(param_folder_path_for_tiff, param_filename)

                    snakes_target_dir = os.path.join(base_output_dir, param_name_extensionless)
                    logging_target_dir = os.path.join(base_logging_dir, param_name_extensionless, image_name_extensionless)

                    make_dir_if_not_exist(snakes_target_dir, logger)
                    make_dir_if_not_exist(logging_target_dir, logger)

                    soax_instance_arg_dicts.append(soax_args_for_tiff_and_param_file(
                        batch_soax_path,
                        image_path,
                        param_filepath,
                        snakes_target_dir,
                        logging_target_dir,
                        delete_soax_logs_for_finished_runs,
                        logger,
                    ))

        # Using sectioned images
        else:
            sectioned_image_folders_info = find_files_or_folders_at_depth(base_image_dir, 0, folders_not_files=True)
            sectioned_image_folder_names = [dirname for containing_path, dirname in sectioned_image_folders_info]

            # Check that there is exactly one param dir for each sectioned image dir
            if len(param_dirnames) != len(sectioned_image_folder_names):
                logger.FAIL(("Expected same number of sectioned image directories as param directories, "
                    "but found {} sectioned image directories in {} and {} param directories in {}").format(
                        len(sectioned_image_folder_names), base_image_dir, len(param_dirnames), base_params_dir,
                ))

            # Match sectioned image directories and param directories together
            for image_num, (param_dirname_for_image, sectioned_image_dirname) in enumerate(zip(param_dirnames, sectioned_image_folder_names)):
                # Check that image name matches with param dir name
                if sectioned_image_dirname != param_dirname_for_image:
                    logger.FAIL(("Parameter folder names in {} and image names in {} don't match: "
                        "At image # {}, {} doesn't match with {}").format(
                            base_params_dir, base_image_dir,
                            image_num, param_dirname_for_image, sectioned_image_dirname
                        ))

                sectioned_image_dirpath = os.path.join(base_image_dir, sectioned_image_dirname)
                param_folder_path_for_image = os.path.join(base_params_dir, param_dirname_for_image)

                image_section_tiff_names = find_tiffs_in_dir(sectioned_image_dirpath)
                param_filenames = find_param_files_in_dir(param_folder_path_for_image)

                for image_section_fn in image_section_tiff_names:
                    image_section_tiff_path = os.path.join(sectioned_image_dirpath, image_section_fn)
                    section_name_extensionless = os.path.splitext(image_section_fn)[0]

                    for param_fn in param_filenames:
                        param_filepath = os.path.join(param_folder_path_for_image, param_fn)
                        param_name_extensionless = os.path.splitext(param_fn)[0]

                        snakes_target_dir = os.path.join(base_output_dir, param_name_extensionless, sectioned_image_dirname)
                        logging_target_dir = os.path.join(base_logging_dir, param_name_extensionless, sectioned_image_dirname, section_name_extensionless)

                        make_dir_if_not_exist(snakes_target_dir, logger)
                        make_dir_if_not_exist(logging_target_dir, logger)

                        soax_instance_arg_dicts.append(soax_args_for_tiff_and_param_file(
                            batch_soax_path,
                            image_section_tiff_path,
                            param_filepath,
                            snakes_target_dir,
                            logging_target_dir,
                            delete_soax_logs_for_finished_runs,
                            logger,
                        ))
    else:
        if not use_sectioned_images:
            tiff_filenames = find_tiffs_in_dir(base_image_dir)

            for tiff_fn in tiff_filenames:
                image_name_extensionless = os.path.splitext(tiff_fn)[0]
                image_path = os.path.join(base_image_dir, tiff_fn)

                param_filenames = find_param_files_in_dir(base_params_dir)

                for param_fn in param_filenames:
                    param_name_extensionless = os.path.splitext(param_fn)[0]
                    param_filepath = os.path.join(base_params_dir, param_fn)

                    snakes_target_dir = os.path.join(base_output_dir, param_name_extensionless)
                    logging_target_dir = os.path.join(base_logging_dir, param_name_extensionless, image_name_extensionless)

                    make_dir_if_not_exist(snakes_target_dir, logger)
                    make_dir_if_not_exist(logging_target_dir, logger)

                    soax_instance_arg_dicts.append(soax_args_for_tiff_and_param_file(
                        batch_soax_path,
                        image_path,
                        param_filepath,
                        snakes_target_dir,
                        logging_target_dir,
                        delete_soax_logs_for_finished_runs,
                        logger,
                    ))
        else:
            sectioned_image_folders_info = find_files_or_folders_at_depth(base_image_dir, 0, folders_not_files=True)
            sectioned_image_folder_names = [dirname for containing_path, dirname in sectioned_image_folders_info]

            for sectioned_image_dirname in sectioned_image_folder_names:
                sectioned_image_dirpath = os.path.join(base_image_dir, sectioned_image_dirname)

                image_section_tiff_names = find_tiffs_in_dir(sectioned_image_dirpath)
                param_filenames = find_param_files_in_dir(base_params_dir)

                for image_section_fn in image_section_tiff_names:
                    image_section_tiff_path = os.path.join(sectioned_image_dirpath, image_section_fn)
                    section_name_extensionless = os.path.splitext(image_section_fn)[0]


                    for param_fn in param_filenames:
                        param_filepath = os.path.join(base_params_dir, param_fn)
                        param_name_extensionless = os.path.splitext(param_fn)[0]

                        snakes_target_dir = os.path.join(base_output_dir, param_name_extensionless, sectioned_image_dirname)
                        logging_target_dir = os.path.join(base_logging_dir, param_name_extensionless, sectioned_image_dirname, section_name_extensionless)

                        make_dir_if_not_exist(snakes_target_dir, logger)
                        make_dir_if_not_exist(logging_target_dir, logger)

                        soax_instance_arg_dicts.append(soax_args_for_tiff_and_param_file(
                            batch_soax_path,
                            image_section_tiff_path,
                            param_filepath,
                            snakes_target_dir,
                            logging_target_dir,
                            delete_soax_logs_for_finished_runs,
                            logger,
                        ))

    with ThreadPool(workers_num) as pool:
        logger.log("Running {} batch_soax workers on {} jobs".format(workers_num, len(soax_instance_arg_dicts)))
        future = pool.map(soax_instance, soax_instance_arg_dicts, chunksize=1)
        logger.log("Finished running batch_soax workers")
