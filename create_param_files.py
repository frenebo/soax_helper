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
        current_val += step

        if current_val > stop:
            break

        if current_val == stop:
            if step != 0:
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

param_abbreviations = {
    "alpha": "a",
    "beta": "b",
    "gamma": "g",
    "min_foreground": "mf",
    "ridge_threshold": "rt",
    "min_snake_length": "msl",
    "gaussian_std": "gstd",
    "snake_point_spacing": "sps",
    "external_factor": "exfac",
    "intensity_scaling": "intscale",
}

def create_param_files(
    target_dir,
    alpha_start_stop_step,
    beta_start_stop_step,
    gamma_start_stop_step,
    min_foreground_start_stop_step,
    ridge_threshold_start_stop_step,
    min_snake_length_start_stop_step,
    gaussian_std_start_stop_step,
    snake_point_spacing_start_stop_step,
    external_factor_start_stop_step,
    intensity_scaling_start_stop_step,
    logger=PrintLogger
    ):
    alphas = create_range(**alpha_start_stop_step)
    betas = create_range(**beta_start_stop_step)
    gammas = create_range(**gamma_start_stop_step)
    min_foregrounds = create_range(**min_foreground_start_stop_step)
    ridge_thresholds = create_range(**ridge_threshold_start_stop_step)
    min_snake_lengths = create_range(**min_snake_length_start_stop_step)
    gaussian_stds = create_range(**gaussian_std_start_stop_step)
    snake_point_spacings = create_range(**snake_point_spacing_start_stop_step)
    external_factors = create_range(**external_factor_start_stop_step)
    intensity_scalings = create_range(**intensity_scaling_start_stop_step)

    alpha_form_settings = param_form_settings(**alpha_start_stop_step)
    beta_form_settings = param_form_settings(**beta_start_stop_step)
    gamma_form_settings = param_form_settings(**gamma_start_stop_step)
    min_foreground_settings = param_form_settings(**min_foreground_start_stop_step)
    ridge_threshold_settings = param_form_settings(**ridge_threshold_start_stop_step)
    min_snake_length_settings = param_form_settings(**min_snake_length_start_stop_step)
    gaussian_std_settings = param_form_settings(**gaussian_std_start_stop_step)
    snake_point_spacing_settings = param_form_settings(**snake_point_spacing_start_stop_step)
    external_factor_settings = param_form_settings(**external_factor_start_stop_step)
    intensity_scaling_settings = param_form_settings(**intensity_scaling_start_stop_step)

    filename_template = "params"
    # For varied param settings we name param files to tell them part
    if len(alphas) > 1:
        print("Alphas: {}".format(alphas))
        filename_template += "_{abbreviation}{{alpha:0{str_length}.{decimals}f}}".format(
            abbreviation=param_abbreviations["alpha"],
            str_length=alpha_form_settings["str_length"],
            decimals=alpha_form_settings["decimal_places"],
        )
    if len(betas) > 1:
        print("Betas: {}".format(betas))
        filename_template += "_{abbreviation}{{beta:0{str_length}.{decimals}f}}".format(
            abbreviation=param_abbreviations["beta"],
            str_length=beta_form_settings["str_length"],
            decimals=beta_form_settings["decimal_places"],
        )
    if len(gammas) > 1:
        filename_template += "_{abbreviation}{{gamma:0{str_length}.{decimals}f}}".format(
            abbreviation=param_abbreviations["gamma"],
            str_length=gamma_form_settings["str_length"],
            decimals=gamma_form_settings["decimal_places"],
        )
    if len(min_foregrounds) > 1:
        filename_template += "_{abbreviation}{{min_foreground:0{str_length}.{decimals}f}}".format(
            abbreviation=param_abbreviations["min_foreground"],
            str_length=min_foreground_settings["str_length"],
            decimals=min_foreground_settings["decimal_places"],
        )
    if len(ridge_thresholds) > 1:
        filename_template += "_{abbreviation}{{ridge_threshold:0{str_length}.{decimals}f}}".format(
            abbreviation=param_abbreviations["ridge_threshold"],
            str_length=ridge_threshold_settings["str_length"],
            decimals=ridge_threshold_settings["decimal_places"],
        )
    if len(min_snake_lengths) > 1:
        filename_template += "_{abbreviation}{{min_snake_length:0{str_length}.{decimals}f}}".format(
            abbreviation=param_abbreviations["min_snake_length"],
            str_length=min_snake_length_settings["str_length"],
            decimals=min_snake_length_settings["decimal_places"],
        )
    if len(gaussian_stds) > 1:
        filename_template += "_{abbreviation}{{gaussian_std:0{str_length}.{decimals}f}}".format(
            abbreviation=param_abbreviations["gaussian_std"],
            str_length=gaussian_std_settings["str_length"],
            decimals=gaussian_std_settings["decimal_places"],
        )
    if len(snake_point_spacings) > 1:
        filename_template += "_{abbreviation}{{snake_point_spacing:0{str_length}.{decimals}f}}".format(
            abbreviation=param_abbreviations["snake_point_spacing"],
            str_length=snake_point_spacing_settings["str_length"],
            decimals=snake_point_spacing_settings["decimal_places"],
        )
    if len(external_factors) > 1:
        filename_template += "_{abbreviation}{{external_factor:0{str_length}.{decimals}f}}".format(
            abbreviation=param_abbreviations["external_factor"],
            str_length=external_factor_settings["str_length"],
            decimals=external_factor_settings["decimal_places"],
        )
    if len(intensity_scalings) > 1:
        filename_template += "_{abbreviation}{{intensity_scaling:0{str_length}.{decimals}f}}".format(
            abbreviation=param_abbreviations["intensity_scaling"],
            str_length=intensity_scaling_settings["str_length"],
            decimals=intensity_scaling_settings["decimal_places"],
        )

    filename_template += ".txt"

    logger.log("Using param filename template {}".format(filename_template))

    # all possible combinations of these parameters
    param_combinations = itertools.product(
        alphas,
        betas,
        gammas,
        min_foregrounds,
        ridge_thresholds,
        min_snake_lengths,
        gaussian_stds,
        snake_point_spacings,
        external_factors,
        intensity_scalings,
    )
    # logger.log("Creating {} different param combinations".format(len(list(param_combinations))))

    for (
        alpha,
        beta,
        gamma,
        min_foreground,
        ridge_threshold,
        min_snake_length,
        gaussian_std,
        snake_point_spacing,
        external_factor,
        inteensity_scaling
    ) in param_combinations:
        params_filename = filename_template.format(
            alpha=alpha,
            beta=beta,
            gamma=gamma,
            min_foreground=min_foreground,
            ridge_threshold=ridge_threshold,
            min_snake_length=min_snake_length,
            gaussian_std=gaussian_std,
            snake_point_spacing=snake_point_spacing,
            external_factor=external_factor,
            intensity_scaling=intensity_scaling,
        )


        fp = os.path.join(target_dir, params_filename)

        params_text = create_params(
            alpha=alpha,
            beta=beta,
            gamma=gamma,
            min_foreground=min_foreground,
            ridge_threshold=ridge_threshold,
            min_snake_length=min_snake_length,
            gaussian_std=gaussian_std,
            snake_point_spacing=snake_point_spacing,
            external_factor=external_factor,
            intensity_scaling=intensity_scaling,
        )

        with open(fp,"w") as file:
            file.write(params_text)
