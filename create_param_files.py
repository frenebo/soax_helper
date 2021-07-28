import argparse
from snakeutils.params import create_params
from snakeutils.files import readable_dir
from snakeutils.logger import PrintLogger
import os
import math
import decimal
import itertools

def error_string_or_parse_arg_or_range(arg):
    split_by_dash = arg.split('-')

    # If we only have one value for this argument instead of a  range
    if len(split_by_dash) == 1:
        try:
            only_val = decimal.Decimal(split_by_dash[0])
        except decimal.InvalidOperation as err:
            return "Expected {} to be decimal number".format(arg) + repr(err)

        start = only_val
        stop = only_val
        step = decimal.Decimal(0)
    else:
        if len(split_by_dash) != 3:
            return "Expected {} to be in form start-stop-step".format(arg)
        try:
            start = decimal.Decimal(split_by_dash[0])
            stop = decimal.Decimal(split_by_dash[1])
            step = decimal.Decimal(split_by_dash[2])
        except decimal.InvalidOperation as err:
            return "Expected {} to be in form start-stop-step. ".format(arg) + repr(err)

    # start of range must be less than or equal to end of range
    if start > stop:
        return "Expected start {} to be <= stop {}".format(start,stop)
    if start != stop and step == 0:
        return "Step cannot be zero"
    if start < 0:
        return "Start value cannot be negative"
    if stop < 0:
        return "Stop value cannot be negative"

    return {"start":start,"stop":stop,"step":step}

# Should be of form 'start-stop-step' or 'value'
def arg_or_range(arg):
    err_str_or_val = error_string_or_parse_arg_or_range(arg)
    if isinstance(err_str_or_val, str):
        raise argparse.ArgumentTypeError(err_str_or_val)
    else:
        return err_str_or_val

def create_range(start,stop,step):
    vals = []
    current_val = start
    while True:
        vals.append(current_val)
        if current_val > stop:
            break
        current_val += step

        if current_val >= stop:
            vals.append(current_val)
            break
    return vals

def param_form_settings(start,stop,step):
    start_exp = start.as_tuple().exponent
    stop_exp = stop.as_tuple().exponent
    step_exp = step.as_tuple().exponent

    decimal_places = - min(start_exp,stop_exp,step_exp)
    if decimal_places < 0:
        decimal_places = 0

    stop_digits_before_decimal_pt = len(stop.as_tuple().digits) + stop_exp
    if decimal_places > 0:
        str_length = stop_digits_before_decimal_pt + 1 + decimal_places
    else:
        str_length = stop_digits_before_decimal_pt

    return {"decimal_places":decimal_places,"str_length": str_length}

def create_params(
    target_dir,
    alpha_start_stop_step,
    beta_start_stop_step,
    min_foreground_start_stop_step,
    ridge_threshold_start_stop_step,
    logger=PrintLogger
    ):
    alphas = create_range(**alpha_start_stop_step)
    betas = create_range(**beta_start_stop_step)
    min_foregrounds = create_range(**min_foreground_start_stop_step)
    ridge_thresholds = create_range(**ridge_threshold_start_stop_step)

    alpha_form_settings = param_form_settings(**alpha_start_stop_step)
    beta_form_settings = param_form_settings(**beta_start_stop_step)
    min_foreground_settings = param_form_settings(**min_foreground_start_stop_step)
    ridge_threshold_settings = param_form_settings(**ridge_threshold_start_stop_step)

    filename_template = "params_a{{alpha:0{}.{}f}}_b{{beta:0{}.{}f}}_mf{{min_foreground:0{}.{}f}}_rt{{ridge_threshold:0{}.{}f}}.txt".format(
        alpha_form_settings["str_length"],
        alpha_form_settings["decimal_places"],
        beta_form_settings["str_length"],
        beta_form_settings["decimal_places"],
        min_foreground_settings["str_length"],
        min_foreground_settings["decimal_places"],
        ridge_threshold_settings["str_length"],
        ridge_threshold_settings["decimal_places"],
    )
    logger.log("Using param filename template {}".format(filename_template))

    # all possible combinations of these parameters
    param_combinations = itertools.product(alphas,betas,min_foregrounds,ridge_thresholds)

    for alpha,beta,min_foreground,ridge_threshold in param_combinations:
        params_filename = filename_template.format(
            alpha=alpha,
            beta=beta,
            min_foreground=min_foreground,
            ridge_threshold=ridge_threshold,
        )

        fp = os.path.join(target_dir, params_filename)

        params_text = create_params(
            alpha=alpha,
            beta=beta,
            min_foreground=min_foreground,
            ridge_threshold=ridge_threshold,
        )

        with open(fp,"w") as file:
            file.write(params_text)


if __name__ == "__main__":
    default_alpha = decimal.Decimal("0.01")
    default_beta = decimal.Decimal("0.1")
    default_min_foreground = decimal.Decimal("0")
    default_ridge_threshold = decimal.Decimal("0.01")
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('target_dir',type=readable_dir,help='Directory for putting created parameter files')
    parser.add_argument('--alpha',
                        type=arg_or_range,
                        default={"start":default_alpha,"stop":default_alpha,"step":decimal.Decimal(0)})
    parser.add_argument('--beta',
                        type=arg_or_range,
                        default={"start":default_beta,"stop":default_beta,"step":decimal.Decimal(0)})
    parser.add_argument('--min_foreground',
                        type=arg_or_range,
                        default={"start":default_min_foreground,"stop":default_min_foreground,"step":decimal.Decimal(0)})
    parser.add_argument('--ridge_threshold',
                        type=arg_or_range,
                        default={"start":default_ridge_threshold,"stop":default_ridge_threshold,"step":decimal.Decimal(0)})


    args = parser.parse_args()

    args.target_dir(
        args.target_dir,
        args.alpha,
        args.beta,
        args.min_foreground,
        args.ridge_threshold,
    )
