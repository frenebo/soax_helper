import argparse
from snakeutils.params import create_params
from snakeutils.files import readable_dir
import os
import math
import decimal

# Should be of form 'start-stop-step' or 'value'
def arg_or_range(arg):
    split_by_dash = arg.split('-')

    # If we only have one value for this argument instead of a  range
    if len(split_by_dash) == 1:
        try:
            only_val = decimal.Decimal(split_by_dash[0])
        except decimal.InvalidOperation as err:
            raise argparse.ArgumentTypeError("Expected {} to be decimal number".format(arg) + repr(err))

        start = only_val
        stop = only_val
        step = decimal.Decimal(0)
    else:
        if len(split_by_dash) != 3:
            raise argparse.ArgumentTypeError("Expected {} to be in form start-stop-step".format(arg))
        try:
            start = decimal.Decimal(split_by_dash[0])
            stop = decimal.Decimal(split_by_dash[1])
            step = decimal.Decimal(split_by_dash[2])
        except decimal.InvalidOperation as err:
            raise argparse.ArgumentTypeError("Expected {} to be in form start-stop-step. ".format(arg) + repr(err))

    # start of range must be less than or equal to end of range
    if start > stop:
        raise argparse.ArgumentTypeError("Expected start {} to be <= stop {}".format(start,stop))
    if start != stop and step == 0:
        raise argparse.ArgumentTypeError("Step cannot be zero")
    if start < 0:
        raise argparse.ArgumentTypeError("Start value cannot be negative")
    if stop < 0:
        raise argparse.ArgumentTypeError("Stop value cannot be negative")

    return {"start":start,"stop":stop,"step":step}

def create_range(start,stop,step):
    vals = []
    current_val = start
    while True:
        vals.append(current_val)
        current_val += step
        print("start{} stop{} step{} current{}".format(start,stop,step,current_val))
        if current_val >= stop:
            break
    return vals

def param_form_settings(start,stop,step):
    start_exp = start.as_tuple().exponent
    stop_exp = stop.as_tuple().exponent
    step_exp = step.as_tuple().exponent
    print(start_exp)
    print(stop_exp)
    print(step_exp)

    decimal_places = - min(start_exp,stop_exp,step_exp)
    if decimal_places < 0:
        decimal_places = 0

    stop_digits_before_decimal_pt = len(stop.as_tuple().digits) + stop_exp
    if decimal_places > 0:
        str_length = stop_digits_before_decimal_pt + 1 + decimal_places
    else:
        str_length = stop_digits_before_decimal_pt

    # print("Start:{} Stop:{} Step:{} decimals:{} strlength: {}")

    return {"decimal_places":decimal_places,"str_length": str_length}


if __name__ == "__main__":
    default_alpha = decimal.Decimal("0.01")
    default_beta = decimal.Decimal("0.1")
    default_min_foreground = decimal.Decimal("0")
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('--alpha',
                        type=arg_or_range,
                        default={"start":default_alpha,"stop":default_alpha,"step":decimal.Decimal(0)})
    parser.add_argument('--beta',
                        type=arg_or_range,
                        default={"start":default_beta,"stop":default_beta,"step":decimal.Decimal(0)})
    parser.add_argument('--min_foreground',
                        type=arg_or_range,
                        default={"start":default_min_foreground,"stop":default_min_foreground,"step":decimal.Decimal(0)})
    parser.add_argument('target_dir',type=readable_dir,help='Directory for putting created parameter files')


    args = parser.parse_args()
    alphas = create_range(**args.alpha)
    betas = create_range(**args.beta)
    min_foregrounds = create_range(**args.min_foreground)

    alpha_form_settings = param_form_settings(**args.alpha)
    beta_form_settings = param_form_settings(**args.beta)
    min_foreground_settings = param_form_settings(**args.min_foreground)

    filename_template = "params_a{{alpha:0{}.{}f}}_b{{beta:0{}.{}f}}_mf{{min_foreground:0{}.{}f}}.txt".format(
        alpha_form_settings["str_length"],
        alpha_form_settings["decimal_places"],
        beta_form_settings["str_length"],
        beta_form_settings["decimal_places"],
        min_foreground_settings["str_length"],
        min_foreground_settings["decimal_places"]
    )
    print(filename_template)

    for alpha in alphas:
        for beta in betas:
            for min_foreground in min_foregrounds:
                params_filename = filename_template.format(alpha=alpha,beta=beta,min_foreground=min_foreground)
                fp = os.path.join(args.target_dir, params_filename)

                params_text = create_params(
                    alpha=alpha,
                    beta=beta,
                    min_foreground=min_foreground
                )

                with open(fp,"w") as file:
                    file.write(params_text)
