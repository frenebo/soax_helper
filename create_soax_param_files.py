from snakeutils.params import create_params
from snakeutils.logger import PrintLogger
import os
import itertools


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

    return str_length, decimal_places

def create_soax_param_files(
    target_dir,
    init_z,
    damp_z,
    intensity_scaling_start_stop_step,
    gaussian_std_start_stop_step,
    ridge_threshold_start_stop_step,
    maximum_foreground_start_stop_step,
    minimum_foreground_start_stop_step,
    snake_point_spacing_start_stop_step,
    min_snake_length_start_stop_step,
    maximum_iterations_start_stop_step,
    change_threshold_start_stop_step,
    check_period_start_stop_step,
    alpha_start_stop_step,
    beta_start_stop_step,
    gamma_start_stop_step,
    external_factor_start_stop_step,
    stretch_factor_start_stop_step,
    number_of_background_radial_sectors_start_stop_step,
    background_z_xy_ratio_start_stop_step,
    radial_near_start_stop_step,
    radial_far_start_stop_step,
    delta_start_stop_step,
    overlap_threshold_start_stop_step,
    grouping_distance_threshold_start_stop_step,
    grouping_delta_start_stop_step,
    minimum_angle_for_soac_linking_start_stop_step,
    logger=PrintLogger
    ):
    raise Exception("Need to create all ranges")

    # Fields that can have start-stop-step values have params created
    # for all possible combos of values
    vary_param_infos = [
        {
            "name": "intensity_scaling",
            "startstopstep": intensity_scaling_start_stop_step,
            "filename_tag": "intscaling",
        },
        {
            "name": "gaussian_std",
            "startstopstep": gaussian_std_start_stop_step,
            "filename_tag": "gstd",
        },
        {
            "name": "ridge_threshold",
            "startstopstep": ridge_threshold_start_stop_step,
            "filename_tag": "rt",
        },
        {
            "name": "maximum_foreground",
            "startstopstep": maximum_foreground_start_stop_step,
            "filename_tag": "maxfore",
        },
        {
            "name": "minimum_foreground",
            "startstopstep": minimum_foreground_start_stop_step,
            "filename_tag": "minfore",
        },
        {
            "name": "snake_point_spacing",
            "startstopstep": snake_point_spacing_start_stop_step,
            "filename_tag": "sps",
        },
        {
            "name": "min_snake_length",
            "startstopstep": min_snake_length_start_stop_step,
            "filename_tag": "minlen",
        },
        {
            "name": "maximum_iterations",
            "startstopstep": maximum_iterations_start_stop_step,
            "filename_tag": "maxiter",
        },
        {
            "name": "change_threshold",
            "startstopstep": change_threshold_start_stop_step,
            "filename_tag": "cngthresh",
        },
        {
            "name": "check_period",
            "startstopstep": check_period_start_stop_step,
            "filename_tag": "ckperiod",
        },
        {
            "name": "alpha",
            "startstopstep": alpha_start_stop_step,
            "filename_tag": "a",
        },
        {
            "name": "beta",
            "startstopstep": beta_start_stop_step,
            "filename_tag": "b",
        },
        {
            "name": "gamma",
            "startstopstep": gamma_start_stop_step,
            "filename_tag": "g",
        },
        {
            "name": "external_factor",
            "startstopstep": external_factor_start_stop_step,
            "filename_tag": "extfac",
        },
        {
            "name": "stretch_factor",
            "startstopstep": stretch_factor_start_stop_step,
            "filename_tag": "stretchfac",
        },
        {
            "name": "number_of_background_radial_sectors",
            "startstopstep": number_of_background_radial_sectors_start_stop_step,
            "filename_tag": "radsectors",
        },
        {
            "name": "background_z_xy_ratio",
            "startstopstep": background_z_xy_ratio_start_stop_step,
            "filename_tag": "zxyratio",
        },
        {
            "name": "radial_near",
            "startstopstep": radial_near_start_stop_step,
            "filename_tag": "rnear",
        },
        {
            "name": "radial_far",
            "startstopstep": radial_far_start_stop_step,
            "filename_tag": "rfar",
        },
        {
            "name": "delta",
            "startstopstep": delta_start_stop_step,
            "filename_tag": "delta",
        },
        {
            "name": "overlap_threshold",
            "startstopstep": overlap_threshold_start_stop_step,
            "filename_tag": "othresh",
        },
        {
            "name": "grouping_distance_threshold",
            "startstopstep": grouping_distance_threshold_start_stop_step,
            "filename_tag": "gdthresh",
        },
        {
            "name": "grouping_delta",
            "startstopstep": grouping_delta_start_stop_step,
            "filename_tag": "gddelta",
        },
        {
            "name": "minimum_angle_for_soac_linking",
            "startstopstep": minimum_angle_for_soac_linking_start_stop_step,
            "filename_tag": "minang",
        },
    ]

    vary_param_values = []

    filename_template = "params"
    for param_info in vary_param_infos:
        # Making list of all values
        param_values = create_range(**param_info["startstopstep"])
        vary_param_values.append(param_values)

        # If there is more than one value for this parameter,
        # we incorporate value into param filename so that parameter files
        # with different parameter values have different names.
        if len(param_values) > 1:
            str_length, decimals = param_form_settings(**param_info["startstopstep"])
            filename_template += "_{filename_tag}{{{name}:0{str_length}.{decimals}f}}".format(
                name=param_info["name"],
                filename_tag=param_info["filename_tag"],
                str_length=str_length,
                decimals=decimals,
            )

    filename_template += ".txt"

    logger.log("Using param filename template {}".format(filename_template))

    # all possible combinations of these parameters
    param_combinations = itertools.product( *  vary_param_values)

    for param_combo in param_combinations:
        param_combo_dict = {}

        for i, param_info in enumerate(vary_param_infos):
            param_combo_dict[param_info["name"]] = param_combo[i]

        params_filename = filename_template.format(**param_combo_dict)

        fp = os.path.join(target_dir, params_filename)

        params_text = create_params(
            init_z=init_z,
            damp_z=damp_z,
            **param_combo_dict,
        )

        with open(fp,"w") as file:
            file.write(params_text)
