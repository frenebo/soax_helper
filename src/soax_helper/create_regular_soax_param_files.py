import os
import itertools
import decimal

from .snakeutils.params import create_params, param_filename_tags

def create_range(start,stop,step):
    start = decimal.Decimal(start)
    stop = decimal.Decimal(stop)
    step = decimal.Decimal(step)

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

def param_filename_string_format_settings(start,stop,step):
    start = decimal.Decimal(start)
    stop = decimal.Decimal(stop)
    step = decimal.Decimal(step)

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

def create_regular_soax_param_files(
    params_save_dir,
    param_settings,
    logger,
    ):

    init_z = param_settings["init_z"]
    damp_z = param_settings["damp_z"]
    intensity_scaling_start_stop_step = param_settings["intensity_scaling"]
    gaussian_std_start_stop_step = param_settings["gaussian_std"]
    ridge_threshold_start_stop_step = param_settings["ridge_threshold"]
    maximum_foreground_start_stop_step = param_settings["maximum_foreground"]
    minimum_foreground_start_stop_step = param_settings["minimum_foreground"]
    snake_point_spacing_start_stop_step = param_settings["snake_point_spacing"]
    min_snake_length_start_stop_step = param_settings["min_snake_length"]
    maximum_iterations_start_stop_step = param_settings["maximum_iterations"]
    change_threshold_start_stop_step = param_settings["change_threshold"]
    check_period_start_stop_step = param_settings["check_period"]
    alpha_start_stop_step = param_settings["alpha"]
    beta_start_stop_step = param_settings["beta"]
    gamma_start_stop_step = param_settings["gamma"]
    external_factor_start_stop_step = param_settings["external_factor"]
    stretch_factor_start_stop_step = param_settings["stretch_factor"]
    number_of_background_radial_sectors_start_stop_step = param_settings["number_of_background_radial_sectors"]
    background_z_xy_ratio_start_stop_step = param_settings["background_z_xy_ratio"]
    radial_near_start_stop_step = param_settings["radial_near"]
    radial_far_start_stop_step = param_settings["radial_far"]
    delta_start_stop_step = param_settings["delta"]
    overlap_threshold_start_stop_step = param_settings["overlap_threshold"]
    grouping_distance_threshold_start_stop_step = param_settings["grouping_distance_threshold"]
    grouping_delta_start_stop_step = param_settings["grouping_delta"]
    minimum_angle_for_soac_linking_start_stop_step = param_settings["minimum_angle_for_soac_linking"]

    # Fields that can have start-stop-step values have params created
    # for all possible combos of values
    vary_param_infos = [
        {
            "name": "intensity_scaling",
            "startstopstep": intensity_scaling_start_stop_step,
        },
        {
            "name": "gaussian_std",
            "startstopstep": gaussian_std_start_stop_step,
        },
        {
            "name": "ridge_threshold",
            "startstopstep": ridge_threshold_start_stop_step,
        },
        {
            "name": "maximum_foreground",
            "startstopstep": maximum_foreground_start_stop_step,
        },
        {
            "name": "minimum_foreground",
            "startstopstep": minimum_foreground_start_stop_step,
        },
        {
            "name": "snake_point_spacing",
            "startstopstep": snake_point_spacing_start_stop_step,
        },
        {
            "name": "min_snake_length",
            "startstopstep": min_snake_length_start_stop_step,
        },
        {
            "name": "maximum_iterations",
            "startstopstep": maximum_iterations_start_stop_step,
        },
        {
            "name": "change_threshold",
            "startstopstep": change_threshold_start_stop_step,
        },
        {
            "name": "check_period",
            "startstopstep": check_period_start_stop_step,
        },
        {
            "name": "alpha",
            "startstopstep": alpha_start_stop_step,
        },
        {
            "name": "beta",
            "startstopstep": beta_start_stop_step,
        },
        {
            "name": "gamma",
            "startstopstep": gamma_start_stop_step,
        },
        {
            "name": "external_factor",
            "startstopstep": external_factor_start_stop_step,
        },
        {
            "name": "stretch_factor",
            "startstopstep": stretch_factor_start_stop_step,
        },
        {
            "name": "number_of_background_radial_sectors",
            "startstopstep": number_of_background_radial_sectors_start_stop_step,
        },
        {
            "name": "background_z_xy_ratio",
            "startstopstep": background_z_xy_ratio_start_stop_step,
        },
        {
            "name": "radial_near",
            "startstopstep": radial_near_start_stop_step,
        },
        {
            "name": "radial_far",
            "startstopstep": radial_far_start_stop_step,
        },
        {
            "name": "delta",
            "startstopstep": delta_start_stop_step,
        },
        {
            "name": "overlap_threshold",
            "startstopstep": overlap_threshold_start_stop_step,
        },
        {
            "name": "grouping_distance_threshold",
            "startstopstep": grouping_distance_threshold_start_stop_step,
        },
        {
            "name": "grouping_delta",
            "startstopstep": grouping_delta_start_stop_step,
        },
        {
            "name": "minimum_angle_for_soac_linking",
            "startstopstep": minimum_angle_for_soac_linking_start_stop_step,
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
            str_length, decimals = param_filename_string_format_settings(**param_info["startstopstep"])
            param_name = param_info["name"]
            filename_tag = param_filename_tags[param_name]
            filename_template += "_{filename_tag}{{{name}:0{str_length}.{decimals}f}}".format(
                name=param_name,
                filename_tag=filename_tag,
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

        fp = os.path.join(params_save_dir, params_filename)

        params_text = create_params(
            init_z=init_z,
            damp_z=damp_z,
            **param_combo_dict,
        )

        with open(fp,"w") as file:
            file.write(params_text)
