import npyscreen
import math
import os
from tiff_info import get_single_tiff_info
from snakeutils.files import find_files_or_folders_at_depth
import numpy as np
import decimal

# For parsing setting strings
class ParseException(Exception):
    pass

# For when you might ask user if they want to make a directory
class DirectoryDoesNotExistParseException(ParseException):
    pass

# For fields that ask for a directory
def check_dir_field(field_name, dir_string, make_dir_if_not_present):
    if dir_string == "":
        raise ParseException("'{}' is a required field".format(field_name))
    if not os.path.isdir(dir_string):
        if os.path.exists(dir_string):
            raise ParseException("'{}' exists but is not a directory".format(dir_string))
        else:
            if make_dir_if_not_present:
                try:
                    os.makedirs(dir_string)
                except Exception as e:
                    raise ParseException("Could not make directory {}: {}".format(dir_string, repr(e)))
            else:
                raise DirectoryDoesNotExistParseException(dir_string)

def check_file_field(field_name, file_path):
    if file_path == "":
        raise ParseException("'{}' is a required field".format(field_name))
    if not os.path.exists(file_path):
        raise ParseException("File '{}' does not exist".format(file_path))
    if not os.path.isfile(file_path):
        raise ParseException("'{}' is not a file".format(file_path))

def parse_int(field_name, field_str):
    if field_str == "":
        raise ParseException("'{}' is a required field".format(field_name))
    try:
        field_val = int(field_str)
    except ValueError as e:
        raise ParseException("Cannot parse '{}' value '{}' as integer: {}".format(field_name,field_str, str(e)))
    return field_val

def parse_pos_int(field_name, field_str):
    field_val = parse_int(field_name, field_str)
    if field_val <= 0:
        raise ParseException("Field '{}' has invalid value '{}': must be positive integer".format(field_name, field_str))
    return field_val

def parse_non_neg_int(field_name, field_str):
    field_val = parse_int(field_name, field_str)
    if field_val < 0:
        raise ParseException("Field '{}' has invalid value '{}': must be non negative integer".format(field_name, field_str))
    return field_val

def parse_pos_float(field_name, field_str):
    if field_str == "":
        raise ParseException("'{}' is a required field".format(field_name))
    try:
        val_float = float(field_str)
    except ValueError as e:
        raise ParseException("Cannot parse '{}' value '{}' as a positive float: {}".format(field_name, field_str, str(e)))

    if val_float <= 0:
        raise ParseException("Invalid '{}' value '{}': Should be positive value".format(field_name, str(val_float)))

    return val_float

def parse_int_coords(field_name, field_str):
    if len(field_str.strip()) == 0:
        raise ParseException("Invalid field '{}' value '{}': value is empty".format(field_name, field_str))

    comma_split = field_str.split(",")
    if len(comma_split) != 3:
        raise ParseException("Could not parse field '{}' value '{}' as three comma-separated integers. Expected 3 items, got {}: {}".format(field_name, field_str, len(comma_split), comma_split))

    val = []
    for item_str in comma_split:
        try:
            item_int = int(item_str)
        except ValueError as int_err:
            try:
                float(item_str)
                is_float = True
            except ValueError:
                is_float = False
            if is_float:
                raise ParseException("Could not parse field '{}' value '{}' as list of integers, list item '{}' is non integer".format(field_name, field_str, item_str))
            else:
                raise ParseException("Could not parse field '{}' value '{}' as list of integers, could not parse list item '{}' as integer: {}".format(field_name, field_str, item_str, str(int_err)))
        if item_int < 0:
            raise ParseException("Invalid field '{}' value '{}': list item '{}' is negative".format(field_name, field_str, item_str))
        val.append(item_int)

    return val

def parse_infer_or_int_coords(field_name, field_str):
    if len(field_str.strip()) == 0:
        raise ParseException("Invalid field '{}' value '{}': value is empty".format(field_name, field_str))

    if field_str.strip().lower() == "infer":
        return {"type": "infer"}

    if "," not in field_str:
        raise ParseException("Invalid field '{}' value '{}': expected string 'infer' or three comma-separated integer (ex. '1,2,3')".format(field_name, field_str))

    val = parse_int_coords(field_name, field_str)

    return {"type": "int_coords", "value": val}

def parse_float_coords(field_name, field_str):
    if len(field_str.strip()) == 0:
        raise ParseException("Invalid field '{}' value '{}': value is empty".format(field_name, field_str))
    # if "," not in field_str:
    #     raise ParseException("Invalid field '{}' value '{}': expected three float values separated by commas".format(field_name, field_str))
    comma_split = field_str.split(",")
    if len(comma_split) != 3:
        raise ParseException("Could not parse field '{}' value '{}' as three comma-separated floats. Expected 3 items, got {}: {}".format(field_name, field_str, len(comma_split), comma_split))

    val = []
    for item_str in comma_split:
        try:
            item_float = float(item_str)
        except ValueError as float_err:
            raise ParseException("Could not parse field '{}' value '{}' as list of floats. Could not parse list item '{}' as float.".format(field_name, field_str, item_str))
        if item_float < 0:
            raise ParseException("Invalid field '{}' value '{}': list item '{}' is negative".format(field_name, field_str, item_str))
        val.append(item_float)
    return val

def error_string_or_arg_or_range(arg, require_int):
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

    if require_int:
        if math.floor(start) != start or math.floor(stop) != stop or math.floor(step) != step:
            return "Expected integer values"

    return {"start":start,"stop":stop,"step":step}

# Should be of form 'start-stop-step' or 'value'
def parse_arg_or_range(field_name, arg, require_int):
    err_str_or_val = error_string_or_arg_or_range(arg, require_int)
    if isinstance(err_str_or_val, str):
        raise ParseException("Error parsing {field_name}: " + err_str_or_val)
    else:
        return err_str_or_val

class SoaxStepsSelectForm(npyscreen.Form):
    def configure(self):
        self.select_steps = self.add(
            npyscreen.TitleMultiSelect,
            max_height =-2,
            value = [],
            name="Pick SOAX Steps (spacebar to toggle)",
            values = [
                "Divide Average Image",
                "Rescale TIFFs in X,Y,Z",
                "Section TIFFs before running SOAX",
                "Make SOAX Parameter Files",
                "Make SOAX Parameter Files - With Image-Specific Parameters",
                "Run SOAX",
                "Convert Snake files to JSON",
                "Join Sectioned Snakes together (you should do this if input images to soax are sectioned)",
                "Make Sindy Fields",
            ],
            scroll_exit=True,
        )

    def afterEditing(self):
        do_divide_average_image              = 0  in self.select_steps.value
        do_rescale                           = 1  in self.select_steps.value
        do_section                           = 2  in self.select_steps.value
        do_create_soax_params                = 3  in self.select_steps.value
        do_create_image_specific_soax_params = 4 in self.select_steps.value
        do_run_soax                          = 4  in self.select_steps.value
        do_snakes_to_json                    = 5  in self.select_steps.value
        do_join_sectioned_snakes             = 6  in self.select_steps.value
        do_make_sindy_fields                 = 7  in self.select_steps.value

        # @TODO do we neeed some other warning for this?
        if do_section:
            if not do_join_sectioned_snakes:
                should_continue = npyscreen.notify_yes_no("If you're sectioning TIFFs, you probably want to join the output snakes of soax in the Join Sectioned Snakes step. Do you want to continue without doing that?", editw=2)
                if not should_continue:
                    return
            if not do_create_image_specific_soax_params:
                should_continue = npyscreen.notify_yes_no("If you're sectioning TIFFs, you need to generate image specific soax parameters: intensity_scaling in SOAX needs to be configured manually for each group of sections from an image. This is so SOAX doesn't auto intensity-scale each image section independently. Continue without doing this?", editw=2)
                if not should_continue:
                    return

        if do_create_soax_params and do_create_image_specific_soax_params:
            npyscreen.notify_confirm("You can't choose to create both types of parameters, pick either 'Make SOAX Parameter Files' or 'Make SOAX Parameter Files - With Image-Specific Parameters'",editw=1)
            return

        self.parentApp.soaxStepsSelectDone(
            do_divide_average_image,
            do_rescale,
            do_section,
            do_create_soax_params,
            do_create_image_specific_soax_params,
            do_run_soax,
            do_snakes_to_json,
            do_join_sectioned_snakes,
            do_make_sindy_fields,
        )

class PIVStepsSelectForm(npyscreen.Form):
    def configure(self):
        self.select_steps = self.add(
            npyscreen.TitleMultiSelect,
            max_height =-2,
            value = [],
            name="Pick PIV Steps (spacebar to toggle)",
            values = [
                "Bead PIV",
            ],
            scroll_exit=True,
        )

    def afterEditing(self):
        do_bead_PIV = 0 in self.select_steps.value

        self.parentApp.PIVStepsSelectDone(
            do_bead_PIV,
        )

class SetupForm(npyscreen.Form):
    field_infos = []
    app_done_func_name = None
    field_strings_nullable_to_grey_out_and_ignore = False

    @staticmethod
    def parseField(field_id, field_str, field_type, field_details, make_dirs_if_not_present):
        if field_type == "dir":
            check_dir_field(field_id, field_str, make_dirs_if_not_present)
            return field_str
        elif field_type == "file":
            check_file_field(field_id, field_str)
            return field_str
        elif field_type == "pos_float":
            return parse_pos_float(field_id, field_str)
        elif field_type == "optional_pos_float":
            if field_str.strip() == "":
                return None
            else:
                return parse_pos_float(field_id, field_str)
        elif field_type == "percentage":
            if field_str == "":
                raise ParseException("'{}' is a required field".format(field_id))
            try:
                perc = float(field_str)
            except ValueError as e:
                raise ParseException("Could not parse '{}' value '{}' as number: {}".format(field_id,field_str, str(e)))

            if perc < 0 or perc > 100:
                raise ParseException("Invalid '{}' value '{}': should be between 0 and 100".format(field_id,str(perc)))

            return perc
        elif field_type == "pos_int":
            return parse_pos_int(field_id, field_str)
        elif field_type == "non_neg_int":
            return parse_non_neg_int(field_id, field_str)
        elif (field_type == "arg_or_range") or (field_type == "int_arg_or_range"):
            require_int = (field_type == "int_arg_or_range")

            if field_str == "":
                raise ParseException("'{}' is a required field")
            try:
                return parse_arg_or_range(field_id, field_str, require_int)
            except AttributeError:
                raise Exception("id: {}, str: {}, require int: {}".format(field_id, field_str, require_int))
        elif field_type == "optional_dir":
            if field_str.strip() == "":
                return None
            else:
                check_dir_field(field_id, field_str, make_dirs_if_not_present)
                return field_str
        elif field_type == "true_false":
            if field_str.lower() != "true" and field_str.lower() != "false":
                raise ParseException("Error parsing {}: value must be 'yes' or 'no', is '{}'".format(field_id, field_str))
            return True if field_str.lower() == "true" else False
        elif field_type == "text":
            if len(field_str.strip()) == 0:
                raise ParseException("Invalid text field '{}' value '{}': value is empty".format(field_id, field_str))
            return field_str
        elif field_type == "letter":
            if len(field_str.strip()) == 0:
                raise ParseException("Invalid letter field '{}' value '{}': value is empty".format(field_id, field_str))
            if len(field_str) != 1:
                raise ParseException("Invalid letter field '{}' value '{}': Expected one character, got".format(field_id, field_str, len(field_str)))
            return field_str
        elif field_type == "int_coords":
            return parse_int_coords(field_id, field_str)
        elif field_type == "infer_or_int_coords":
            return parse_infer_or_int_coords(field_id, field_str)
        elif field_type == "float_coords":
            return parse_float_coords(field_id, field_str)
        else:
            raise Exception("Unknown field type '{}'".format(field_type))

    @classmethod
    def parseSettings(cls, field_strings, make_dirs_if_not_present):
        parsed_fields = {}

        for field_info in cls.field_infos:
            field_id = field_info["id"]
            field_type = field_info["type"]
            field_str = field_strings[field_id]
            field_details = field_info["details"] if "details" in field_info else None
            if cls.field_strings_nullable_to_grey_out_and_ignore and field_str is None:
                parsed_fields[field_id] = None
            else:
                parsed_fields[field_id] = cls.parseField(field_id, field_str, field_type, field_details, make_dirs_if_not_present)

        return parsed_fields

    def add_info_text(self, info_str):
        self.add(npyscreen.FixedText, value=info_str)

    def add_field(self, field_id, field_name, field_str, field_type):
        if self.field_strings_nullable_to_grey_out_and_ignore and field_str is None:
            self.npy_fields[field_id] = self.add(
                npyscreen.TitleText,
                name=field_name,
                value="Field Disabled",
                editable=False)
        elif field_type in [
            "dir",
            "optional_dir",
            "file",
        ]:
            self.npy_fields[field_id] = self.add(
                npyscreen.TitleFilename,
                name=field_name,
                value=field_str,
            )
        elif field_type in [
            "pos_float",
            "optional_pos_float",
            "percentage",
            "pos_int",
            "non_neg_int",
            "arg_or_range",
            "int_arg_or_range",
            "text",
            "letter",
            "int_coords",
            "infer_or_int_coords",
            "float_coords",
        ]:
            self.npy_fields[field_id] = self.add(
                npyscreen.TitleText,
                name=field_name,
                value=field_str)
        elif field_type == "true_false":
            self.npy_fields[field_id] = self.add(
                npyscreen.TitleSelectOne,
                max_height = 3,
                name=field_name,
                values=["true", "false"],
                value=([0] if field_str == "true" else [1]),
                scroll_exit=True)
        else:
            raise Exception("Unknown type '{}' for field '{}'".format(field_type, field_id))

    def configure(self, menu_config, make_dirs_if_not_present):
        field_defaults = menu_config["fields"]
        self.npy_fields = {}
        self.make_dirs_if_not_present = make_dirs_if_not_present

        for field_info in self.field_infos:
            if "help" in field_info:
                if type(field_info["help"]) == list:
                    for info_str in field_info["help"]:
                        self.add_info_text(info_str)
                else:
                    self.add_info_text(field_info["help"])

            field_id = field_info["id"]
            if "name" in field_info:
                field_name = field_info["name"]
            else:
                field_name = field_id
            if field_id in menu_config["notes"]:
                self.add_info_text(menu_config["notes"][field_id])
            field_str = field_defaults[field_id]
            field_type = field_info["type"]

            self.add_field(field_id, field_name, field_str, field_type)


    def getFieldString(self, field_type, field_id, field_details):
        if field_type in [
            "dir",
            "optional_dir",
            "file",
            "pos_float",
            "optional_pos_float",
            "percentage",
            "pos_int",
            "non_neg_int",
            "arg_or_range",
            "int_arg_or_range",
            "text",
            "letter",
            "int_coords",
            "infer_or_int_coords",
            "float_coords",
        ]:
            return self.npy_fields[field_id].value
        elif field_type in ["true_false"]:
            return "true" if (0 in self.npy_fields[field_id].value) else "false"
        else:
            raise Exception("Don't know what to do with field_type {}".format(field_type))

    def getFieldStrings(self):
        field_strings = {}

        for field_info in self.field_infos:
            field_id = field_info["id"]
            field_type = field_info["type"]
            field_details = field_info["details"] if "details" in field_info else None

            field_str = self.getFieldString(field_type, field_id, field_details)
            field_strings[field_id] = field_str

        return field_strings

    def afterEditing(self):
        try:
            self.parseSettings(self.getFieldStrings(), self.make_dirs_if_not_present)
        except ParseException as e:
            if isinstance(e, DirectoryDoesNotExistParseException):
                dirpath = str(e)
                should_make_dir = npyscreen.notify_yes_no("Directory {} does not exist. Create? (Select No to return to setup page)".format(dirpath), editw=1)
                # Make dirs and try again
                if should_make_dir:
                    os.makedirs(dirpath)
                    self.afterEditing()
                    return
                # Just send user back to menu by returning
                else:
                    return
            # Show user error, then send user bacck to menu by returning
            else:
                npyscreen.notify_confirm(str(e),editw=1)
                return
        if not hasattr(self, "app_done_func_name"):
            raise Exception("Parent app does not have a done function named '{}'".format(app_done_func_name))
        if self.app_done_func_name is None:
            raise Exception("Class isissing app_done_func_name to call with argument strings")
        setup_done_func = getattr(self.parentApp, self.app_done_func_name)

        setup_done_func(self.getFieldStrings())

class PixelSizeSelectionForm(SetupForm):
    field_infos = [
        {
            "id": "x_spacing",
            "name": "Pixel Width Spacing (um)",
            "type": "pos_float",
        },
        {
            "id": "y_spacing",
            "name": "Pixel Height Spacing (um)",
            "type": "pos_float",
        },
        {
            "id": "z_spacing",
            "name": "Pixel Z-Stack Depth Spacing (um)",
            "type": "pos_float",
        },
    ]

    app_done_func_name = "pixelSizeSelectDone"

class DivideAverageImageSetupForm(SetupForm):
    field_infos = [
        {
            "id": "source_tiff_dir",
            "type": "dir",
            "help": "Take average image over all data, and divide the average (to remove constant background noise, if possible)",
        },
        {
            "id": "target_tiff_dir",
            "type": "dir",
        },
    ]

    app_done_func_name = "divideAverageImageSetupDone"

class RescaleSetupForm(SetupForm):
    field_infos = [
        {
            "id": "source_tiff_dir",
            "type": "dir",
        },
        {
            "id": "target_tiff_dir",
            "type": "dir",
        },
        {
            "id": "input_dims",
            "help": "Dimensions of the input tiffs from source_tiff_dir (width,height,depth)",
            "type": "int_coords",
        },
        {
            "id": "output_dims",
            "help": "Dimensions to resize tiffs to (width,height,depth)",
            "type": "int_coords"
        },
        {
            "id": "workers_num",
            "type": "pos_int",
        },
    ]

    app_done_func_name = "rescaleSetupDone"

class SectioningSetupForm(SetupForm):
    field_infos = [
        {
            "id": "source_tiff_dir",
            "type": "dir",
        },
        {
            "id": "target_sectioned_tiff_dir",
            "type": "dir",
        },
        {
            "id": "section_max_size",
            "type": "pos_int",
            "help": [
                "Maximum size of a section in pixels (in width, length, height). ",
                "Will divide into as many pieces for pieces to be smaller than ",
                "this section_max_size in all dimensions.",
            ],
        },
        {
            "id": "workers_num",
            "type": "pos_int",
        },
    ]

    app_done_func_name = "sectioningSetupDone"

# class SoaxParamsFirstPageForm(SetupForm):
#     field_infos = [
#         {
#             "id": "params_save_dir",
#             "type": "dir",
#         },
#         {
#             "id": "make_params_for_individual_images",
#             "type": "true_false",
#         },
#     ]

#     app_done_func_name = "soaxParamsSetupFirstPageDone"

        # self.create_normal_soax_params_config = {
        #     "fields": {
        #         "params_save_dir": "./Params",
        #     },
        #     "notes": {},
        # }

class CreateNormalSoaxParamsSetupForm(SetupForm):
    # @TODO add help info about following param pages
    field_infos = [
        {
            "id": "params_save_dir",
            "type": "dir",
        },
    ]
    app_done_func_name = "createNormalSoaxParamsSetupDone"

class CreateImageSpecificSoaxParamsSetupForm(SetupForm):
    # @TODO add help info about following param pages
    field_infos = [
        {
            "id": "params_save_dir",
            "type": "dir",
        },
        # @TODO make optional????
        {
            "id": "original_tiff_dir",
            "type": "dir",
        },
        {
            "id": "set_intensity_scaling_for_each_image",
            "type": "true_false",
        },
    ]

    app_done_func_name = "createImageSpecificSoaxParamsSetupDone"

class SoaxParamsSetupPage1Form(SetupForm):
    field_infos = [
        {
            "id": "gaussian_std",
            "type": "arg_or_range",
            "help": [
                "Enter SOAX run parameters to try.",
                "For number fields, enter individual values (ex. '1','3.44', or '10.3') or start-stop-step ranges (ex. '1-20-0.5' or '1.5-3.5-1.0')",
                "If ranges are given, soax will be run multiple times, trying all combinations of parameter values",
            ],
        },
        {
            "id": "ridge_threshold",
            "type": "arg_or_range",
        },
        {
            "id": "intensity_scaling",
            "type": "arg_or_range",
            "help": [
                "Intensity scaling controls how SOAX rescales image brightness. 0=automatic rescaling",
                "If input images have been intensity-scaled in a previous step, we don't want SOAX to rescale brightness",
                "If the input TIFFs are 16 bit, set intensity_scaling to 1/65535 = 0.000015259. to rescale from TIFF max intensity to 1.0 max intensity",
                "If input images are sectioned before feeding to SOAX, they should be intensity rescaled",
                "before sectioning, so intensity processing on all sections is uniform",
            ],
        },
        {
            "id": "maximum_foreground",
            "type": "int_arg_or_range",
        },
        {
            "id": "minimum_foreground",
            "type": "int_arg_or_range",
        },
    ]

    field_strings_nullable_to_grey_out_and_ignore = True

    app_done_func_name = "soaxParamsSetupPage1Done"

class SoaxParamsSetupPage2Form(SetupForm):
    field_infos = [
        {
            "id": "init_z",
            "type": "true_false",
        },
        {
            "id": "snake_point_spacing",
            "type": "arg_or_range",
        },
        {
            "id": "min_snake_length",
            "type": "arg_or_range",
        },
        {
            "id": "maximum_iterations",
            "type": "int_arg_or_range",
        },
        {
            "id": "change_threshold",
            "type": "arg_or_range",
        },
        {
            "id": "check_period",
            "type": "int_arg_or_range",
        },
        {
            "id": "alpha",
            "type": "arg_or_range",
        },
        {
            "id": "beta",
            "type": "arg_or_range",
        },
        {
            "id": "gamma",
            "type": "arg_or_range",
        },
        {
            "id": "external_factor",
            "type": "arg_or_range",
        },
        {
            "id": "stretch_factor",
            "type": "arg_or_range",
        },
    ]

    field_strings_nullable_to_grey_out_and_ignore = True

    app_done_func_name = "soaxParamsSetupPage2Done"

class SoaxParamsSetupPage3Form(SetupForm):
    field_infos = [
        {
            "id": "number_of_background_radial_sectors",
            "type": "int_arg_or_range",
        },
        {
            "id": "background_z_xy_ratio",
            "type": "arg_or_range",
        },
        {
            "id": "radial_near",
            "type": "arg_or_range",
        },
        {
            "id": "radial_far",
            "type": "arg_or_range",
        },
        {
            "id": "delta",
            "type": "int_arg_or_range",
        },
        {
            "id": "overlap_threshold",
            "type": "arg_or_range",
        },
        {
            "id": "grouping_distance_threshold",
            "type": "arg_or_range",
        },
        {
            "id": "grouping_delta",
            "type": "int_arg_or_range",
        },
        {
            "id": "minimum_angle_for_soac_linking",
            "type": "arg_or_range",
        },
        {
            "id": "damp_z",
            "type": "true_false",
        },
    ]

    field_strings_nullable_to_grey_out_and_ignore = True

    app_done_func_name = "soaxParamsSetupPage3Done"

class SoaxRunSetupForm(SetupForm):
    field_infos = [
        {
            "id": "source_tiff_dir",
            "type": "dir",
        },
        {
            "id": "target_snakes_dir",
            "type": "dir",
        },
        {
            "id": "param_files_dir",
            "type": "dir",
        },
        {
            "id": "use_image_specific_params",
            "type": "true_false",
        },
        {
            "id": "soax_log_dir",
            "type": "dir",
        },
        {
            "id": "batch_soax_path",
            "type": "file",
        },
        {
            "id": "workers",
            "type": "pos_int",
        },
        {
            "help": [
                "If you don't care about the SOAX print-out logs for",
                "finished runs that had no errors, set this to true",
            ],
            "id": "delete_soax_logs_for_finished_runs",
            "type": "true_false",
        },
        {
            "id": "use_sectioned_images",
            "type": "true_false",
        },
    ]

    app_done_func_name = "soaxRunSetupDone"

class SnakesToJsonSetupForm(SetupForm):
    field_infos = [
        {
            "id": "source_snakes_dir",
            "type": "dir",
        },
        {
            "id": "target_json_dir",
            "type": "dir",
        },
        {
            "id": "source_snakes_depth",
            "type": "non_neg_int",
        },
        {
            "id": "offset_pixels",
            "type": "infer_or_int_coords",
            "help": [
                "Offset pixels is useful if the snakes from SOAX are for a section of the original TIFF image. If the snakes were",
                "calculated from a TIFF section that went from x=100 to x=200, y=150 to y=300, z=30 to z=80, then the offset pixels",
                "would be 100,150,30. If the snakes are for the entire image, input '0,0,0'. If the input images were cut up in the",
                "sectioning step, then the image filenames and SOAX snake filenames should contain the coordinates of each section,",
                "and the snakes to JSON converter can infer offset from filename. In that case input '0,0,0'",
            ],
        },
        {
            "id": "dims_pixels",
            "type": "infer_or_int_coords",
            "help": [
                "The x,y,z dimensions of the input TIFF (or TIFF section). Ex. '100,200,40'",
                "Similar to offset_pixels, enter 'infer' if processing TIFF section snakes."
            ],
        },
        {
            "id": "pixel_spacing_um_xyz",
            "type": "float_coords",
        },
    ]

    app_done_func_name = "snakesToJsonSetupDone"

class JoinSectionedSnakesSetupForm(SetupForm):
    field_infos = [
        {
            "id": "source_json_dir",
            "type": "dir",
            "help": [
                "Join JSON snake files from sections of an image",
                "to form JSON files with all the snakes from original images",
            ],
        },
        {
            "id": "target_json_dir",
            "type": "dir",
        },
        {
            "id": "source_jsons_depth",
            "type": "non_neg_int",
        },
        {
            "id": "workers",
            "type": "pos_int",
        }
    ]

    app_done_func_name = "joinSectionedSnakesSetupDone"

class MakeSindyFieldsSetupForm(SetupForm):
    field_infos = [
        {
            "id": "source_json_dir",
            "type": "dir",
        },
        {
            "id": "source_jsons_depth",
            "type": "non_neg_int",
        },
        {
            "id": "source_images_dir",
            "type": "dir",
        },
        {
            "id": "save_intensities_dir",
            "type": "dir",
        },
        {
            "id": "save_orientations_dir",
            "type": "dir",
        },
    ]

    app_done_func_name = "makeSindyFieldsSetupDone"

class BeadPIVSetupForm(SetupForm):
    field_infos = [
        {
            "id":"source_tiff_dir",
            "type": "dir",
        },
        {
            "id": "tiff_fn_letter_before_frame_num",
            "type": "letter",
            "help": [
                "The source TIFF files should have names like fileName0.tif, fileName1.tif, etc. The library that trackpy uses to read the TIFFs in sequence requires the letter that comes",
                "before the number in each tiff filename. For 'fileName##.tif', the letter would be 'e' since that's the last letter in 'fileName' before the number starts."
            ],
        },
        {
            "id":"target_piv_data_dir",
            "type": "dir",
        },
        {
            "id": "bead_diameter_um",
            "type": "pos_float",
        },
        {
            "id": "x_y_pixel_size_um",
            "type": "pos_float",
        },
        {
            "id": "z_stack_spacing_um",
            "type": "pos_float",
        },
        {
            "help": [
                "Search distance for tracking beads.",
                "Trackpy library tries to match beads from one time point to the next,",
                "looking in the next time point for a bead within this distance from where the bead",
                "was in the previous frame.",
                "Value should be larger than the distance beads will move from one frame to another",
            ],
            "id": "linking_search_range_um",
            "type": "pos_float",
        }
    ]

    app_done_func_name = "beadPIVSetupDone"

class SoaxSetupApp(npyscreen.NPSAppManaged):
    def __init__(self, make_dirs=False, **kwargs):
        super().__init__(**kwargs)
        self.make_dirs = make_dirs

    def onStart(self):
        # Default configurations for setup forms, including default fields to show in forms.

        self.divide_average_image_config = {
            "fields": {
                "source_tiff_dir": "",
                "target_tiff_dir": "./AverageImageDividedTIFFs",
            },
            "notes": {},
        }
        self.rescale_config = {
            "fields": {
                "source_tiff_dir": "",
                "target_tiff_dir": "./RescaledTIFFs",
                "input_dims": "",
                "output_dims": "",
                "workers_num": "1",
            },
            "notes": {},
        }
        self.sectioning_config = {
            "fields": {
                "source_tiff_dir": "",
                "target_sectioned_tiff_dir": "./SectionedTIFFs",
                "section_max_size": "200",
                "workers_num": "1",
            },
            "notes": {},
        }

        self.create_normal_soax_params_config = {
            "fields": {
                "params_save_dir": "./Params",
            },
            "notes": {},
        }

        self.create_image_specific_soax_params_config = {
            "fields": {
                "params_save_dir": "./ImageSpecificParams",

                "original_tiff_dir": "",

                "set_intensity_scaling_for_each_image": "false",
            },
            "notes": {},
        }

        # self.soax_params_first_page_config = {
        #     "fields": {
        #         "params_save_dir": "./Params",
        #         "make_params_for_individual_images": "false",
        #     },
        #     "notes": {},
        # }

        # self.soax_params_page1_config = {
        #     "fields": {
        #         "params_save_dir": "./Params",
        #         "intensity_scaling": "0",
        #         "gaussian_std": "0",
        #         "ridge_threshold": "0.01",
        #         "maximum_foreground": "65535",
        #         "minimum_foreground": "0",
        #     },
        #     "notes": {},
        # }
        # self.soax_params_page2_config = {
        #     "fields": {
        #         "init_z": "true",
        #         "snake_point_spacing": "1",
        #         "min_snake_length": "10",
        #         "maximum_iterations": "10000",
        #         "change_threshold": "0.1",
        #         "check_period": "100",
        #         "alpha": "0.01",
        #         "beta": "0.1",
        #         "gamma": "2",
        #         "external_factor": "1",
        #         "stretch_factor": "0.2",
        #     },
        #     "notes": {},
        # }
        # self.soax_params_page3_config = {
        #     "fields": {
        #         "number_of_background_radial_sectors": "8",
        #         "background_z_xy_ratio": "2.88",
        #         "radial_near": "4",
        #         "radial_far": "8",
        #         "delta": "4",
        #         "overlap_threshold": "1",
        #         "grouping_distance_threshold": "4",
        #         "grouping_delta": "8",
        #         "minimum_angle_for_soac_linking": "2.1",
        #         "damp_z": "false",
        #     },
        #     "notes": {},
        # }

        # In Ubuntu 20.04, to build SOAX, I followed the steps from https://www.lehigh.edu/~div206/soax/downloads.html
        # under the section "Building SOAX in Windows Linux Subsystem (Ubuntu 18.04.1 LTS)"
        # With the change that I had to install libphonon-dev from https://packages.ubuntu.com/bionic/libphonon-dev
        # and also install some dependencies of libphonon dev from source

        self.soax_run_config = {
            "fields":  {
                "workers": "1",
                "use_sectioned_images": "false",
                "batch_soax_path": "/home/paul/Documents/build_soax_july3_follow_ubuntu_18_guide/build_soax_3.7.2/batch_soax",
                "source_tiff_dir": "",
                "target_snakes_dir": "./Snakes",
                "delete_soax_logs_for_finished_runs": "false",
                "param_files_dir": "",
                "use_image_specific_params": "false",
                "soax_log_dir": "./SoaxLogs",
            },
            "notes": {},
        }
        self.snakes_to_json_config = {
            "fields": {
                "source_snakes_dir": "",
                "target_json_dir": "./JsonSnakes",
                "source_snakes_depth": "",
                "offset_pixels": "0,0,0",
                "dims_pixels": "",
                "pixel_spacing_um_xyz": "",
            },
            "notes": {},
        }
        self.join_sectioned_snakes_config = {
            "fields": {
                "source_json_dir": "",
                "target_json_dir": "./JoinedJsonSnakes",
                "source_jsons_depth": "",
                "workers": "1",
            },
            "notes": {},
        }
        self.make_sindy_fields_config = {
            "fields": {
                "source_json_dir": "",
                "source_jsons_depth": "",
                "source_images_dir": "",
                "save_intensities_dir": "./IntensityFields",
                "save_orientations_dir": "./OrientationFields",
            },
            "notes": {},
        }

        self.bead_PIV_config = {
            "fields": {
                "x_y_pixel_size_um": "",
                "z_stack_spacing_um": "",
                "source_tiff_dir": "",
                "tiff_fn_letter_before_frame_num": "",
                "target_piv_data_dir": "./BeadPIVsData",
                "bead_diameter_um": "",
                "linking_search_range_um": "3",
            },
            "notes": {},
        }

        self.pixel_spacing_xyz = None
        self.image_dims = None
        self.image_being_split = False

        self.menu_functions = [
            self.startSoaxStepsSelect,
            self.startPIVStepsSelect,
        ]
        self.form_index = -1

        self.goToNextMenu()

    def getActionConfigs(self):
        action_configs = []
        if self.do_divide_average_image:
            action_configs.append({
                "action": "divide_average_image",
                "settings": self.divide_average_image_config["fields"],
            })
        if self.do_rescale:
            action_configs.append({
                "action": "rescale_tiffs",
                "settings": self.rescale_config["fields"],
            })
        if self.do_section:
            action_configs.append({
                "action": "section_tiffs",
                "settings": self.sectioning_config["fields"],
            })
        if self.do_create_soax_params:
            # @TODO params
            action_configs.append({
                "action": "create_soax_param_files",
                "settings": {
                    **self.create_normal_soax_params_config["fields"],
                    "param_fields": {
                        **self.soax_params_page1_config["fields"],
                        **self.soax_params_page2_config["fields"],
                        **self.soax_params_page3_config["fields"],
                    },
                },
            })
        if self.do_create_image_specific_soax_params:
            action_configs.append({
                "action": "create_image_specific_params_files",
                "settings": {
                    **self.create_image_specific_soax_params_config["fields"],
                    "param_fields": {
                        **self.soax_params_page1_config["fields"],
                        **self.soax_params_page2_config["fields"],
                        **self.soax_params_page3_config["fields"],
                    },
                }
            })
            pass
        if self.do_run_soax:
            action_configs.append({
                "action": "run_soax",
                "settings": self.soax_run_config["fields"],
            })
        if self.do_snakes_to_json:
            action_configs.append({
                "action": "convert_snakes_to_json",
                "settings": self.snakes_to_json_config["fields"],
            })
        if self.do_join_sectioned_snakes:
            action_configs.append({
                "action": "join_sectioned_snakes",
                "settings": self.join_sectioned_snakes_config["fields"],
            })
        if self.do_make_sindy_fields:
            action_configs.append({
                "action": "make_sindy_fields",
                "settings": self.make_sindy_fields_config["fields"],
            })
        if self.do_bead_PIV:
            action_configs.append({
                "action": "do_bead_PIV",
                "settings": self.bead_PIV_config["fields"],
            })
        return action_configs

    def try_find_dir_first_tif_metadata(self, tiff_dir, img_depth):
        if not os.path.isdir(tiff_dir):
            return None

        image_locations_info = find_files_or_folders_at_depth(tiff_dir, img_depth, file_extensions=[".tiff", ".tif"])

        if len(image_locations_info) == 0:
            return None

        first_img_dir = image_locations_info[0][0]
        first_img_fn = image_locations_info[0][1]
        first_img_fp = os.path.join(first_img_dir, first_img_fn)

        shape, z_size, dtype = get_single_tiff_info(first_img_fp)
        y_size, x_size = shape

        return {
            "tif_name": first_img_fn,
            "tif_path": first_img_fp,
            "dims": [x_size,y_size,z_size],
            "tif_max_level": np.iinfo(dtype).max,
        }

    def goToNextMenu(self):
        self.form_index += 1
        if self.form_index >= len(self.menu_functions):
            self.setNextForm(None)
        else:
            next_menu_func = self.menu_functions[self.form_index]
            next_menu_func()

    def prompt_pixel_size_if_not_known(self, tiff_folder_name):
        if self.pixel_spacing_xyz is not None:
            return
        if not self.do_snakes_to_json:
            return

        should_enter_pixel_size = npyscreen.notify_yes_no("The size of a pixel in micrometers (from images in {}) will be needed to format output data. Do you want to input pixel size now?".format(tiff_folder_name), editw=2)
        if should_enter_pixel_size:
            self.menu_functions.insert(self.form_index + 1, self.startPixelSizeSelect)

    def startPixelSizeSelect(self):
        self.addForm('PIXEL_SIZE_SELECT', PixelSizeSelectionForm, name="Select Pixel Size")
        self.getForm('PIXEL_SIZE_SELECT').configure(
            {
                "fields":  {
                    "x_spacing": "",
                    "y_spacing": "",
                    "z_spacing": "",
                },
                "notes": {},
            },
            self.make_dirs,
        )
        self.setNextForm('PIXEL_SIZE_SELECT')

    def pixelSizeSelectDone(self, fields):
        parsed_fields = PixelSizeSelectionForm.parseSettings(fields, self.make_dirs)

        self.pixel_spacing_xyz = [
            parsed_fields["x_spacing"],
            parsed_fields["y_spacing"],
            parsed_fields["z_spacing"],
        ]

        self.goToNextMenu()

    def startSoaxStepsSelect(self):
        self.addForm('SOAX_STEPS_SELECT', SoaxStepsSelectForm, name='Select Soax Steps')
        self.getForm('SOAX_STEPS_SELECT').configure()
        self.setNextForm('SOAX_STEPS_SELECT')

    def soaxStepsSelectDone(self,
        do_divide_average_image,
        do_rescale,
        do_section,
        do_create_soax_params,
        do_create_image_specific_soax_params,
        do_run_soax,
        do_snakes_to_json,
        do_join_sectioned_snakes,
        do_make_sindy_fields,
        ):
        self.do_divide_average_image = do_divide_average_image
        self.do_rescale = do_rescale
        self.do_section = do_section
        self.do_create_soax_params = do_create_soax_params
        self.do_create_image_specific_soax_params = do_create_image_specific_soax_params
        self.do_run_soax = do_run_soax
        self.do_snakes_to_json = do_snakes_to_json
        self.do_join_sectioned_snakes = do_join_sectioned_snakes
        self.do_make_sindy_fields = do_make_sindy_fields

        if self.do_divide_average_image:
            self.menu_functions.append(self.startDivideAverageImageSetup)
        if self.do_rescale:
            self.menu_functions.append(self.startRescaleSetup)
        if self.do_section:
            self.menu_functions.append(self.startSectioningSetup)
        if self.do_create_soax_params:
            self.menu_functions.append(self.startCreateNormalSoaxParamsSetup)
            self.menu_functions.append(self.startSoaxParamsSelectPage1)
            self.menu_functions.append(self.startSoaxParamsSelectPage2)
            self.menu_functions.append(self.startSoaxParamsSelectPage3)
        if self.do_create_image_specific_soax_params:
            self.menu_functions.append(self.startCreateImageSpecificSoaxParamsSetup)
            self.menu_functions.append(self.startSoaxParamsSelectPage1)
            self.menu_functions.append(self.startSoaxParamsSelectPage2)
            self.menu_functions.append(self.startSoaxParamsSelectPage3)
        if self.do_run_soax:
            self.menu_functions.append(self.startSoaxRunSetup)
        if self.do_snakes_to_json:
            self.menu_functions.append(self.startSnakesToJsonSetup)
        if self.do_join_sectioned_snakes:
            self.menu_functions.append(self.startJoinSectionedSnakesSetup)
        if self.do_make_sindy_fields:
            self.menu_functions.append(self.startMakeSindyFieldsSetup)

        # Move onto next index
        self.goToNextMenu()

    def startPIVStepsSelect(self):
        self.addForm('PIV_STEPS_SELECT', PIVStepsSelectForm, name='Select PIV Steps')
        self.getForm('PIV_STEPS_SELECT').configure()
        self.setNextForm('PIV_STEPS_SELECT')

    def PIVStepsSelectDone(self,
        do_bead_PIV,
        ):
        self.do_bead_PIV = do_bead_PIV

        if self.do_bead_PIV:
            self.menu_functions.append(self.startBeadPIVSetup)

        self.goToNextMenu()

    def setOrigTiffDirForImageSpecificParamsIfNotSet(self, tiff_dirpath):
        if self.create_image_specific_soax_params_config["fields"]["original_tiff_dir"] == "":
            self.create_image_specific_soax_params_config["fields"]["original_tiff_dir"] = tiff_dirpath

    def determineImageDimsFromDirIfNotKnown(self, dirpath):
        if self.image_dims is not None:
            return

        img_search_depth = 0

        tif_metadata = self.try_find_dir_first_tif_metadata(dirpath, img_search_depth)
        if tif_metadata is not None:
            self.image_dims = tif_metadata["dims"]

    # @TODO sort out where all this goes
    # def startIntensityScalingSetup(self):
    #     self.addForm('INTENSITY_SCALING_SETUP', IntensityScalingSetupForm, name='Intensity Scaling Setup')
    #     self.getForm('INTENSITY_SCALING_SETUP').configure(self.intensity_scaling_config, self.make_dirs)
    #     self.setNextForm('INTENSITY_SCALING_SETUP')

    # def intensityScalingSetupDone(self, fields):
    #     self.intensity_scaling_config["fields"] = fields

    #     self.divide_average_image_config["fields"]["source_tiff_dir"] = fields["target_tiff_dir"]
    #     self.rescale_config["fields"]["source_tiff_dir"] = fields["target_tiff_dir"]
    #     self.sectioning_config["fields"]["source_tiff_dir"] = fields["target_tiff_dir"]
    #     self.soax_run_config["fields"]["source_tiff_dir"] = fields["target_tiff_dir"]

    #     # If input TIFFs have been rescaled to range from 0 to 65535,
    #     # When SOAX runs and converts to floats, intensities should be rescaled from 0 to 1.0
    #     # We can't have 0.0 to 1.0 scale in original TIFFs because TIFFs have only integer brightness
    #     # levels
    #     img_search_depth = 0
    #     tif_metadata = self.try_find_dir_first_tif_metadata(
    #         fields["source_tiff_dir"],
    #         img_search_depth,
    #     )

    #     if tif_metadata is None:
    #         npyscreen.notify_confirm(
    #             "In soax run stage intensity_scaling will need to be set manually, could not find TIFF files in {} at depth {} to set intensity to 1 / tiff data type max value".format(fields["source_tiff_dir"], img_search_depth),
    #             wide=True,
    #             editw=1)
    #     else:
    #         tif_max_level = tif_metadata["tif_max_level"]
    #         # @TODO params
    #         # self.soax_params_page1_config["fields"]["intensity_scaling"] = format(1/tif_max_level, '.5f')
    #         # self.soax_params_page1_config["notes"]["intensity_scaling"] = "Set intensity scaling to 1/{max_lev} because max brightness in tiff {tif_path} is {max_lev} (From input to Intensity Scaling step)".format(
    #         #     max_lev=tif_max_level,
    #         #     tif_path=tif_metadata["tif_path"],
    #         # )
    #         self.rescale_config["fields"]["input_dims"] = ",".join([str(dim) for dim in tif_metadata["dims"]])

    #     self.prompt_pixel_size_if_not_known(fields["source_tiff_dir"])
    #     self.determineImageDimsFromDirIfNotKnown(fields["source_tiff_dir"])

    #     self.goToNextMenu()

    def startDivideAverageImageSetup(self):
        self.addForm('DIVIDE_AVERAGE_IMAGE_SETUP', DivideAverageImageSetupForm, name='Divide Average Image Setup')
        self.getForm('DIVIDE_AVERAGE_IMAGE_SETUP').configure(self.divide_average_image_config, self.make_dirs)
        self.setNextForm('DIVIDE_AVERAGE_IMAGE_SETUP')

    def divideAverageImageSetupDone(self, fields):
        self.divide_average_image_config["fields"] = fields

        self.rescale_config["fields"]["source_tiff_dir"] = fields["target_tiff_dir"]
        self.sectioning_config["fields"]["source_tiff_dir"] = fields["target_tiff_dir"]
        self.soax_run_config["fields"]["source_tiff_dir"] = fields["target_tiff_dir"]

        self.prompt_pixel_size_if_not_known(fields["source_tiff_dir"])
        self.determineImageDimsFromDirIfNotKnown(fields["source_tiff_dir"])
        self.setOrigTiffDirForImageSpecificParamsIfNotSet(fields["source_tiff_dir"])

        self.goToNextMenu()

    def startRescaleSetup(self):
        self.addForm('RESCALE_SETUP', RescaleSetupForm, name='Rescale Setup')
        self.getForm('RESCALE_SETUP').configure(self.rescale_config, self.make_dirs)
        self.setNextForm('RESCALE_SETUP')

    def rescaleSetupDone(self, fields):
        self.rescale_config["fields"] = fields

        self.sectioning_config["fields"]["source_tiff_dir"] = fields["target_tiff_dir"]
        self.soax_run_config["fields"]["source_tiff_dir"] = fields["target_tiff_dir"]

        orig_dims = parse_int_coords(".", fields["input_dims"])
        new_dims = parse_int_coords(".", fields["output_dims"])

        if self.pixel_spacing_xyz is not None:
            new_x_space = self.pixel_spacing_xyz[0] * orig_dims[0] / new_dims[0]
            new_y_space = self.pixel_spacing_xyz[1] * orig_dims[1] / new_dims[1]
            new_z_space = self.pixel_spacing_xyz[2] * orig_dims[2] / new_dims[2]
            self.pixel_spacing_xyz = [new_x_space,new_y_space,new_z_space]
        else:
            self.prompt_pixel_size_if_not_known(fields["target_tiff_dir"])

        self.image_dims = new_dims

        self.setOrigTiffDirForImageSpecificParamsIfNotSet(fields["source_tiff_dir"])

        self.goToNextMenu()

    def startSectioningSetup(self):
        self.addForm('SECTIONING_SETUP', SectioningSetupForm, name='Sectioning Setup')
        self.getForm('SECTIONING_SETUP').configure(self.sectioning_config, self.make_dirs)
        self.setNextForm('SECTIONING_SETUP')

    def sectioningSetupDone(self, fields):
        self.sectioning_config["fields"] = fields
        self.soax_run_config["fields"]["source_tiff_dir"] = fields["target_sectioned_tiff_dir"]
        self.soax_run_config["fields"]["use_sectioned_images"] = "true"
        self.soax_run_config["fields"]["use_image_specific_params"] = "true"
        self.create_image_specific_soax_params_config["fields"]["set_intensity_scaling_for_each_image"] = "true"

        self.image_being_split = True

        self.prompt_pixel_size_if_not_known(fields["source_tiff_dir"])
        self.determineImageDimsFromDirIfNotKnown(fields["source_tiff_dir"])

        self.goToNextMenu()

    def startCreateNormalSoaxParamsSetup(self):
        self.addForm('CREATE_NORMAL_SOAX_PARAMS_SETUP', CreateNormalSoaxParamsSetupForm, name='Create Soax Params Setup Form')
        self.getForm('CREATE_NORMAL_SOAX_PARAMS_SETUP').configure(self.create_normal_soax_params_config)
        self.setNextForm('CREATE_NORMAL_SOAX_PARAMS_SETUP')

    def createNormalSoaxParamsSetupDone(self, fields):
        self.create_normal_soax_params_config["fields"] = fields
        self.goToNextMenu()

    def startCreateImageSpecificSoaxParamsSetup(self):
        self.addForm('CREATE_IMAGE_SPECIFIC_SOAX_PARAMS_SETUP', CreateImageSpecificSoaxParamsSetupForm, name='Create Image Specific Soax Params Setup Form')
        self.getForm('CREATE_IMAGE_SPECIFIC_SOAX_PARAMS_SETUP').configure(self.create_image_specific_soax_params_config)
        self.setNextForm('CREATE_IMAGE_SPECIFIC_SOAX_PARAMS_SETUP')

    def createImageSpecificSoaxParamsSetupDone(self, fields):
        self.create_image_specific_soax_params_config["fields"] = fields

        if fields["set_intensity_scaling_for_each_image"] == "true":
            self.soax_params_page1_config["intensity_scaling"] = None

        self.goToNextMenu()

    def startSoaxParamsSetupPage1(self):
        self.addForm('PARAM_SETUP_PAGE_1', SoaxParamsSetupPage1Form, name="SOAX Params Setup Page 1/3")
        self.getForm('PARAM_SETUP_PAGE_1').configure(self.soax_params_page1_config, self.make_dirs)
        self.setNextForm('PARAM_SETUP_PAGE_1')

    def soaxParamsSetupPage1Done(self, fields):
        self.soax_params_page1_config["fields"] = fields
        self.soax_run_config["fields"]["param_files_dir"] = fields["params_save_dir"]
        self.goToNextMenu()

    def startSoaxParamsSetupPage2(self):
        self.addForm('PARAM_SETUP_PAGE_2', SoaxParamsSetupPage2Form, name="SOAX Params Setup Page 2/3")
        self.getForm('PARAM_SETUP_PAGE_2').configure(self.soax_params_page2_config, self.make_dirs)
        self.setNextForm('PARAM_SETUP_PAGE_2')

    def soaxParamsSetupPage2Done(self, fields):
        self.soax_params_page2_config["fields"] = fields
        self.goToNextMenu()

    def startSoaxParamsSetupPage3(self):
        self.addForm('PARAM_SETUP_PAGE_3', SoaxParamsSetupPage3Form, name="SOAX Params Setup Page 3/3")
        self.getForm('PARAM_SETUP_PAGE_3').configure(self.soax_params_page3_config, self.make_dirs)
        self.setNextForm('PARAM_SETUP_PAGE_3')

    def soaxParamsSetupPage3Done(self, fields):
        self.soax_params_page3_config["fields"] = fields
        self.goToNextMenu()

    def startSoaxRunSetup(self):
        self.addForm('SOAX_RUN_SETUP', SoaxRunSetupForm, name="SOAX Run Setup")
        self.getForm('SOAX_RUN_SETUP').configure(self.soax_run_config, self.make_dirs)
        self.setNextForm('SOAX_RUN_SETUP')

    def soaxRunSetupDone(self, fields):
        self.soax_run_config["fields"] = fields
        self.snakes_to_json_config["fields"]["source_snakes_dir"] = fields["target_snakes_dir"]

        if fields["use_sectioned_images"] == "true":
            self.snakes_to_json_config["fields"]["source_snakes_depth"] = "2"
        else:
            self.snakes_to_json_config["fields"]["source_snakes_depth"] = "1"

        self.prompt_pixel_size_if_not_known(fields["source_tiff_dir"])

        self.goToNextMenu()

    def startSnakesToJsonSetup(self):
        if self.pixel_spacing_xyz is not None:
            spacing_string = ",".join([str(dim) for dim in self.pixel_spacing_xyz])
            self.snakes_to_json_config["fields"]["pixel_spacing_um_xyz"] = spacing_string
            self.snakes_to_json_config["notes"]["pixel_spacing_um_xyz"] = "Set from previously input data (and rescale factor if applicable)"

        if self.image_being_split:
            self.snakes_to_json_config["fields"]["dims_pixels"] = "infer"
            self.snakes_to_json_config["fields"]["offset_pixels"] = "infer"
        elif self.image_dims is not None:
            pixel_dims_string = ",".join([str(dim) for dim in self.image_dims])
            self.snakes_to_json_config["fields"]["dims_pixels"] = pixel_dims_string

        self.addForm('SNAKES_TO_JSON_SETUP', SnakesToJsonSetupForm, name="Snakes to JSON Setup")
        self.getForm('SNAKES_TO_JSON_SETUP').configure(self.snakes_to_json_config, self.make_dirs)
        self.setNextForm('SNAKES_TO_JSON_SETUP')

    def snakesToJsonSetupDone(self, config):
        self.snakes_to_json_config["fields"] = config

        target_json_dir = config["target_json_dir"]
        self.join_sectioned_snakes_config["fields"]["source_json_dir"] = target_json_dir
        self.make_sindy_fields_config["fields"]["source_json_dir"] = target_json_dir

        output_jsons_depth = config["source_snakes_depth"]
        self.join_sectioned_snakes_config["fields"]["source_jsons_depth"] = output_jsons_depth
        self.make_sindy_fields_config["fields"]["source_json_dir"] = output_jsons_depth

        self.goToNextMenu()

    def startJoinSectionedSnakesSetup(self):
        self.addForm('JOIN_SECTIONED_SNAKES_SETUP', JoinSectionedSnakesSetupForm, name="Join Sectioned Snakes Setup")
        self.getForm('JOIN_SECTIONED_SNAKES_SETUP').configure(self.join_sectioned_snakes_config, self.make_dirs)
        self.setNextForm('JOIN_SECTIONED_SNAKES_SETUP')

    def joinSectionedSnakesSetupDone(self, fields):
        self.join_sectioned_snakes_config["fields"] = fields

        target_json_dir = fields["target_json_dir"]
        self.make_sindy_fields_config["fields"]["source_json_dir"] = target_json_dir

        # Output jsons are one directory less deep since they've been joined
        output_jsons_depth = str(int(fields["source_jsons_depth"]) - 1)
        self.make_sindy_fields_config["fields"]["source_json_dir"] = output_jsons_depth

        self.goToNextMenu()

    def startMakeSindyFieldsSetup(self):
        self.addForm('MAKE_SINDY_FIELDS', MakeSindyFieldsSetupForm, name="Make Sindy Fields Setup")
        self.getForm('MAKE_SINDY_FIELDS').configure(self.make_sindy_fields_config, self.make_dirs)
        self.setNextForm('MAKE_SINDY_FIELDS')

    def makeSindyFieldsSetupDone(self, fields):
        self.make_sindy_fields_config["fields"] = fields
        self.goToNextMenu()

    def startBeadPIVSetup(self):
        self.addForm('BEAD_PIV_SETUP', BeadPIVSetupForm, name="Bead PIV Setup")
        self.getForm('BEAD_PIV_SETUP').configure(self.bead_PIV_config, self.make_dirs)
        self.setNextForm('BEAD_PIV_SETUP')

    def beadPIVSetupDone(self, fields):
        self.bead_PIV_config["fields"] = fields
        self.goToNextMenu()
