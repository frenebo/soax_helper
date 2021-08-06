from snakeutils.logger import PrintLogger
import subprocess

def z_rescale_tiffs(batch_resample_path, source_dir, target_dir, rescale_factor, logger=PrintLogger):
    ret_code = subprocess.run([batch_resample, source_dir, target_dir, str(rescale_factor)])

    if ret_code != 0:
        logger.FAIL("'{}' failed with return code {}".format(batch_resample_path, ret_code))