from create_soax_param_files import error_string_or_parse_arg_or_range, create_soax_param_files
import npyscreen
import os
from tiff_info import get_single_tiff_info
from snakeutils.files import find_files_or_folders_at_depth
import numpy as np

# For parsing setting strings
class ParseException(Exception):
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
                raise ParseException("Directory '{}' does not exist".format(dir_string))

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
        raise ParseException("Cannot parse '{}' value '{}' as integer".format(field_name,field_str))
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
    except ValueError:
        raise ParseException("'{}' value '{}' is not a float".format(field_name, field_str))

    if val_float <= 0:
        raise ParseException("Invalid '{}' value '{}': Should be positive value".format(field_name, str(val_float)))

    return val_float

class SoaxStepsSelectForm(npyscreen.Form):
    def configure(self):
        self.select_steps = self.add(
            npyscreen.TitleMultiSelect,
            max_height =-2,
            value = [],
            name="Pick SOAX Steps (spacebar to toggle)",
            values = [
                "Auto Contrast Raw TIFFs",
                "Rescale TIFFs in X,Y,Z",
                # "Rescale TIFFs in X and Y",
                "Section TIFFs before running SOAX",
                "Create Parameter Files",
                "Run SOAX",
                "Convert Snake files to JSON",
                "Join Sectioned Snakes together (you should do this if input images to soax are sectioned)",
                "Scale JSON snakes to real length units",
                "Make Orientation Fields",
            ],
            scroll_exit=True,
        )

    def afterEditing(self):
        do_auto_contrast                   = 0  in self.select_steps.value
        do_rescale                         = 1  in self.select_steps.value
        do_section                         = 2  in self.select_steps.value
        do_create_soax_params              = 3  in self.select_steps.value
        do_run_soax                        = 4  in self.select_steps.value
        do_snakes_to_json                  = 5  in self.select_steps.value
        do_join_sectioned_snakes           = 6  in self.select_steps.value
        do_scale_json_snakes_to_units      = 7  in self.select_steps.value
        do_make_orientation_fields         = 8  in self.select_steps.value

        self.parentApp.soaxStepsSelectDone(
            do_auto_contrast,
            do_rescale,
            do_section,
            do_create_soax_params,
            do_run_soax,
            do_snakes_to_json,
            do_join_sectioned_snakes,
            do_scale_json_snakes_to_units,
            do_make_orientation_fields,
        )

class PIVStepsSelectForm(npyscreen.Form):
    def configure(self):
        self.select_steps = self.add(
            npyscreen.TitleMultiSelect,
            max_height =-2,
            value = [],
            name="Pick PIV Steps (spacebar to toggle)",
            values = [
                "Auto Contrast Bead TIFFs for PIV",
                "Auto Contrast Tube TIFFs for PIV",
                "Bead PIV",
                "Tube PIV",
            ],
            scroll_exit=True,
        )

    def afterEditing(self):
        do_bead_piv_auto_contrast = 0 in self.select_steps.value
        do_tube_piv_auto_contrast = 1 in self.select_steps.value
        do_bead_PIV               = 2 in self.select_steps.value
        do_tube_PIV               = 3 in self.select_steps.value

        self.parentApp.PIVStepsSelectDone(
            do_bead_piv_auto_contrast,
            do_tube_piv_auto_contrast,
            do_bead_PIV,
            do_tube_PIV,
        )

class SetupForm(npyscreen.Form):
    field_infos = []
    app_done_func_name = None

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
            except ValueError:
                raise ParseException("'{}' value '{}' is not a number".format(field_id,field_str))

            if perc < 0 or perc > 100:
                raise ParseException("Invalid '{}' value '{}': should be between 0 and 100".format(field_id,str(perc)))

            return perc
        elif field_type == "pos_int":
            return parse_pos_int(field_id, field_str)
        elif field_type == "non_neg_int":
            return parse_non_neg_int(field_id, field_str)
        elif field_type ==  "arg_or_range":
            if field_str == "":
                raise ParseException("'{}' is a required field")

            err_str_or_val = error_string_or_parse_arg_or_range(field_str)
            if isinstance(err_str_or_val, str):
                raise ParseException("Error parsing {}: {}".format(field_id, err_str_or_val))
            else:
                return err_str_or_val
        elif field_type == "optional_dir":
            if field_str.strip() == "":
                return None
            else:
                check_dir_field(field_id, field_str, make_dirs_if_not_present)
                return field_str
        elif field_type == "yes_no":
            if field_str != "yes" and field_str != "no":
                raise ParseException("Error parsing {}: value must be 'yes' or 'no', is '{}'".format(field_id, field_str))
            return True if field_str == "yes" else False
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

            parsed_fields[field_id] = cls.parseField(field_id, field_str, field_type, field_details, make_dirs_if_not_present)

        return parsed_fields

    def add_info_text(self, info_str):
        self.add(npyscreen.FixedText, value=info_str)

    def add_field(self, field_id, field_name, field_str, field_type):
        if field_type in [
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
            "text",
            "letter",
        ]:
            self.npy_fields[field_id] = self.add(
                npyscreen.TitleText,
                name=field_name,
                value=field_str)
        elif field_type == "yes_no":
            self.npy_fields[field_id] = self.add(
                npyscreen.TitleSelectOne,
                max_height = 3,
                name=field_name,
                values=["yes", "no"],
                value=([0] if field_str == "yes" else [1]),
                scroll_exit=True)
        else:
            raise Exception("Unknown type '{}' for field '{}'".format(field_type, field_id))

    def configure(self, field_defaults, make_dirs_if_not_present):
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
            "text",
            "letter",
        ]:
            return self.npy_fields[field_id].value
        elif field_type in ["yes_no"]:
            return "yes" if (0 in self.npy_fields[field_id].value) else "no"

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
            npyscreen.notify_confirm(str(e),editw=1)
            return
        if not hasattr(self, "app_done_func_name"):
            raise Exception("Parent app does not have a done function named '{}'".format(app_done_func_name))
        if self.app_done_func_name is None:
            raise Exception("Class isissing app_done_func_name to call with argument strings")
        setup_done_func = getattr(self.parentApp, self.app_done_func_name)

        setup_done_func(self.getFieldStrings())

class RescaleSetupForm(SetupForm):
    field_infos = [
        {
            "id": "batch_resample_path",
            "type": "file",
        },
        {
            "help": "Rescale z-axis depth of images using SOAX batch_resample. Useful if making images smaller or correcting for z-slice size",
            "id": "source_tiff_dir",
            "type": "dir",
        },
        {
            "id": "target_tiff_dir",
            "type": "dir",
        },
        {
            "id": "xy_factor",
            "type": "pos_float",
        },
        {
            "id": "z_factor",
            "type": "pos_float",
        },
    ]

    app_done_func_name = "RescaleSetupDone"


class AutoContrastSetupForm(SetupForm):
    field_infos = [
        {
            "id": "source_tiff_dir",
            "type": "dir",
            "help": [
                "Min and max cutoff percent are brightness level percentiles to use to rescale the TIFF image brightnesses ",
                "min=1 and max=99 would find the brightness that only 1% of tiff pixels in the first TIF in the directory are dimmer than, ",
                "and the brightness that 99% of tiff pixels are dimmer than. The 1% brightness is the lower threshold, and 99% brightness is the upper threhold. ",
                "All pixels dimmer than the lower threshold are set to total black, all pixels brighter than the upper threshold are set to pure white, ",
                "and pixel brightnesses in between are rescaled to a new value between total black and total white",
            ],
        },
        {
            "id": "target_tiff_dir",
            "type": "dir",
        },
        {
            "id": "min_cutoff_percent",
            "type": "percentage",
        },
        {
            "id": "max_cutoff_percent",
            "type": "percentage",
        },
        {
            "id": "workers_num",
            "type": "pos_int",
        },
    ]

    app_done_func_name = "autoContrastSetupDone"

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
        }
    ]

    app_done_func_name = "sectioningSetupDone"

class SoaxParamsSetupPage1Form(SetupForm):
    field_infos = [
        {
            "id": "params_save_dir",
            "type": "dir",
            "help": [
                "Enter SOAX run parameters to try.",
                "Enter number values (ex. 1,3.44,10.3) or start-stop-step ranges (ex. 1-20-0.5,1.5-3.5-1.0)",
                "If ranges are given, soax will be run multiple times, trying all combinations of parameter values",
            ],
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
            "id": "min_foreground",
            "type": "arg_or_range",
        },
        {
            "id": "ridge_threshold",
            "type": "arg_or_range",
        },
        {
            "id": "min_snake_length",
            "type": "arg_or_range",
        },
    ]

    app_done_func_name = "soaxParamsSetupPage1Done"

class SoaxParamsSetupPage2Form(SetupForm):
    field_infos = [
        {
            "id": "gaussian_std",
            "type": "arg_or_range",
        },
        {
            "id": "snake_point_spacing",
            "type": "arg_or_range",
        },
        {
            "id": "external_factor",
            "type": "arg_or_range",
        },
        {
            "id": "intensity_scaling",
            "type": "arg_or_range",
            "help": [
                "Intensity scaling controls how SOAX rescales image brightness. 0=automatic rescaling",
                "If input images have been contrast-scaled in a previous step, we don't want SOAX to rescale brightness",
                "If the input TIFs are 16 bit, set intensity_scaling to 1/65535 = 0.000015259. to rescale from TIF max intensity to 1.0 max intensity",
                "If input images are sectioned before feeding to SOAX, they should be contrast rescaled",
                "before sectioning, so all sections have same contrast setting",
            ],
        },
        {
            "id": "stretch_factor",
            "type": "arg_or_range",
        },
    ]

    app_done_func_name = "soaxParamsSetupPage2Done"

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
            "id": "use_subdirs",
            "type": "yes_no"
        }
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
        }
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
        }
    ]

    app_done_func_name = "joinSectionedSnakesSetupDone"

class ScaleJsonSnakesToUnitsSetupForm(SetupForm):
    field_infos = [
        {
            "id": "source_json_dir",
            "type": "dir",
            "help": "Take json snakes with pixel coordinate values and convert to real length units",
        },
        {
            "id": "target_json_dir",
            "type": "dir",
        },
        {
            "id": "source_jsons_depth",
            "type": "non_neg_int"
        },
        {
            "id": "x_y_pixel_size_um",
            "type": "pos_float",
            "help": "x_y_pixel_size_um is the size of a single pixel in the original TIFF image",
        },
        {
            "id": "x_y_image_scale_factor",
            "type": "pos_float",
            "help": [
                "If image was rescaled in x and y before being run to soax, enter scale factor here",
                "(ex. 0.5 for half sized image scale) to account for changed pixel size when calculating real length",
            ],
        },
        {
            "id": "z_stack_spacing_um",
            "name": "z_stack_spacing_um (if applicable)",
            "type": "optional_pos_float",
            "help": "The distance between z stacks in source TIFF images",
        },
        {
            "id": "unit_abbreviation",
            "type": "text"
        }
    ]

    app_done_func_name = "scaleJsonSnakesToUnitsSetupDone"

class MakeOrientationFieldsSetupForm(SetupForm):
    field_infos = [
        {
            "id": "source_json_dir",
            "type": "dir",
        },
        {
            "id": "target_data_dir",
            "type": "dir",
        },
        {
            "id": "source_jsons_depth",
            "type": "non_neg_int",
        },
        {
            "id": "image_width",
            "type": "pos_int",
        },
        {
            "id": "image_height",
            "type": "pos_int",
        },
    ]

    app_done_func_name = "makeOrientationFieldsSetupDone"

class BeadPivAutoContrastSetupForm(AutoContrastSetupForm):
    app_done_func_name = "beadPivAutoContrastSetupDone"

class TubePivAutoContrastSetupForm(AutoContrastSetupForm):
    app_done_func_name = "tubePivAutoContrastSetupDone"

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
            "id": "x_y_pixel_size_um",
            "type": "pos_float",
            "help": "x_y_pixel_size_um is the size of a single pixel in the original TIFF image",
        },
        {
            "id": "z_stack_spacing_um",
            "type": "pos_float",
            "help": "The distance between z stacks in source TIFF images",
        },
        {
            "id": "bead_diameter_um",
            "type": "pos_float",
        },
    ]

    app_done_func_name = "beadPIVSetupDone"

class TubePIVSetupForm(SetupForm):
    field_infos = [
        {
            "id": "source_tiff_dir",
            "type": "dir",
        },
        {
            "id": "target_piv_data_dir",
            "type": "dir",
        },
    ]

    app_done_func_name = "tubePIVSetupDone"

class SoaxSetupApp(npyscreen.NPSAppManaged):
    def __init__(self, make_dirs=False, **kwargs):
        super().__init__(**kwargs)

    def onStart(self):
        # Default settings to show in forms. Updated by user and by setup app,
        # like automatically setting source_tiff_dir of rescale_settings to target_tiff_ddir of auto contrast
        # if user configures auto contrast
        self.auto_contrast_settings = {
            "max_cutoff_percent": "95.5",
            "min_cutoff_percent": "0.1",
            "workers_num": "1",
            "source_tiff_dir": "",
            "target_tiff_dir": "./AutoContrastedTIFFs",
        }
        self.rescale_settings = {
            "batch_resample_path": "/home/paul/Documents/build_soax_july3_follow_ubuntu_18_guide/build_soax_3.7.2/batch_resample",
            "source_tiff_dir": "",
            "target_tiff_dir": "RescaledTIFFs",
            "xy_factor": "1.0",
            "z_factor": "1.0",
        }
        self.sectioning_settings = {
            "source_tiff_dir": "",
            "target_sectioned_tiff_dir": "./SectionedTIFFs",
            "section_max_size": "200",
        }
        self.soax_params_page1_settings = {
            "params_save_dir": "./Params",
            "alpha": "0.01",
            "beta": "0.1",
            "gamma": "2",
            "min_foreground":"10",
            "ridge_threshold":"0.01",
            "min_snake_length":"20",
        }
        self.soax_params_page2_settings = {
            "gaussian_std":"0",
            "snake_point_spacing":"5",
            "external_factor":"1",
            "intensity_scaling": "0",
            "stretch_factor": "0.2",
        }
        self.soax_run_settings = {
            "workers": "1",
            "use_subdirs": "no",
            "batch_soax_path": "/home/paul/Documents/build_soax_july3_follow_ubuntu_18_guide/build_soax_3.7.2/batch_soax",
            "source_tiff_dir": "",
            "target_snakes_dir": "./Snakes",
            "param_files_dir": "",
            "soax_log_dir": "./SoaxLogs",
        }
        self.snakes_to_json_settings = {
            "source_snakes_dir": "",
            "target_json_dir": "./JsonSnakes",
            "source_snakes_depth": "",
        }
        self.join_sectioned_snakes_settings = {
            "source_json_dir": "",
            "target_json_dir": "./JoinedJsonSnakes",
            "source_jsons_depth": "",
        }
        self.scale_json_snakes_to_units_settings = {
            "source_json_dir": "",
            "target_json_dir": "./UnitScaledJsonSnakes",
            "source_jsons_depth": "",
            "x_y_pixel_size_um": "",
            "x_y_image_scale_factor": "",
            "z_stack_spacing_um": "",
            "unit_abbreviation": "",
        }
        self.make_orientation_fields_settings = {
            "source_json_dir": "",
            "source_jsons_depth": "",
            "target_data_dir": "./OrientationFields",
            "image_width": "",
            "image_height": "",
        }

        #PIV settings
        self.bead_piv_auto_contrast_settings = {
            "max_cutoff_percent": "95.5",
            "min_cutoff_percent": "0.1",
            "workers_num": "1",
            "source_tiff_dir": "",
            "target_tiff_dir": "./AutoContrastedBeadTIFFsForPIV",
        }
        self.tube_piv_auto_contrast_settings = {
            "max_cutoff_percent": "95.5",
            "min_cutoff_percent": "0.1",
            "workers_num": "1",
            "source_tiff_dir": "",
            "target_tiff_dir": "./AutoContrastedTubeTIFFsForPIV",
        }
        self.bead_PIV_settings = {
            "source_tiff_dir": "",
            "tiff_fn_letter_before_frame_num": "",
            "target_piv_data_dir": "./BeadPIVsData",
            "x_y_pixel_size_um": "",
            "z_stack_spacing_um": "",
            "bead_diameter_um": "",
        }
        self.tube_PIV_settings = {
            "source_tiff_dir": "",
            "target_piv_data_dir": "./TubePIVData",
        }

        self.menu_functions = [
            self.startSoaxStepsSelect,
            self.startPIVStepsSelect,
        ]
        self.form_index = -1

        self.goToNextMenu()

    def getActionConfigs(self):
        action_configs = []
        if self.do_auto_contrast:
            action_configs.append({
                "action": "auto_contrast_tiffs",
                "settings": self.auto_contrast_settings,
            })
        if self.do_rescale:
            action_configs.append({
                "action": "rescale_tiffs",
                "settings": self.rescale_settings,
            })
        if self.do_section:
            action_configs.append({
                "action": "section_tiffs",
                "settings": self.sectioning_settings,
            })
        if self.do_create_soax_params:
            action_configs.append({
                "action": "create_soax_param_files",
                # Combine page 1 and page 2 settings
                "settings": {
                    **self.soax_params_page1_settings,
                    **self.soax_params_page2_settings,
                },
            })
        if self.do_run_soax:
            action_configs.append({
                "action": "run_soax",
                "settings": self.soax_run_settings,
            })
        if self.do_snakes_to_json:
            action_configs.append({
                "action": "convert_snakes_to_json",
                "settings": self.snakes_to_json_settings,
            })
        if self.do_join_sectioned_snakes:
            action_configs.append({
                "action": "join_sectioned_snakes",
                "settings": self.join_sectioned_snakes_settings,
            })
        if self.do_scale_json_snakes_to_units:
            action_configs.append({
                "action": "scale_json_snakes_to_units",
                "settings": self.scale_json_snakes_to_units_settings,
            })
        if self.do_make_orientation_fields:
            action_configs.append({
                "action": "make_orientation_fields",
                "settings": self.make_orientation_fields_settings,
            })
        # if self.do_make_sindy_matrices_from_snakes:
        #     action_configs.append({
        #         "action": "make_sindy_matrices_from_snakes",
        #         "settings": self.make_sindy_matrices_from_snakes_settings,
        #     })
        if self.do_bead_piv_auto_contrast:
            action_configs.append({
                "action": "auto_contrast_tiffs",
                "settings": self.bead_piv_auto_contrast_settings,
            })
        if self.do_tube_piv_auto_contrast:
            action_configs.append({
                "action": "auto_contrast_tiffs",
                "settings": self.tube_piv_auto_contrast_settings,
            })
        if self.do_bead_PIV:
            action_configs.append({
                "action": "do_bead_PIV",
                "settings": self.bead_PIV_settings,
            })
        if self.do_tube_PIV:
            action_configs.append({
                "action": "do_tube_PIV",
                "settings": self.tube_PIV_settings,
            })
        return action_configs

    def first_img_fp(self, tiff_dir, img_depth):
        image_locations_info = find_files_or_folders_at_depth(tiff_dir, img_depth, file_extensions=[".tiff", ".tif"])

        #If source tiff dir doesn't have anything at this depth, we won't do anything here
        if len(image_locations_info) == 0:
            return None
        first_img_dir = image_locations_info[0][0]
        first_img_name = image_locations_info[0][1]
        first_img_fp = os.path.join(first_img_dir, first_img_name)

        return first_img_fp

    def get_first_tif_data_type_max(self, tiff_dir, img_depth):
        first_img_fp = self.first_img_fp(tiff_dir, img_depth)
        if first_img_fp is None:
            return None
        shape, stack_height, dtype = get_single_tiff_info(first_img_fp)
        return np.iinfo(dtype).max

    # def auto_set_width_height_images_settings(self, tiff_dir, img_depth, rescale_factor=None):
    #     first_img_fp = self.first_img_fp(tiff_dir, img_depth)
    #     if first_img_fp is None:
    #         npyscreen.notify_confirm(
    #             "Cannot determine width and height of images, you'll have to set those manually if needed later. No images found in {} at depth {}".format(tiff_dir, img_depth),
    #             editw=1,
    #         )
    #         return
    #     shape, stack_height, dtype = get_single_tiff_info(first_img_fp)
    #     width, height = shape
    #     if rescale_factor is not None:
    #         width = int(width * rescale_factor)
    #         height = int(height * rescale_factor)
    #     self.make_snake_images_settings["width"] = str(width)
    #     self.make_snake_images_settings["height"] = str(height)

    def goToNextMenu(self):
        self.form_index += 1
        if self.form_index >= len(self.menu_functions):
            self.setNextForm(None)
        else:
            next_menu_func = self.menu_functions[self.form_index]
            next_menu_func()

    def startSoaxStepsSelect(self):
        self.addForm('SOAX_STEPS_SELECT', SoaxStepsSelectForm, name='Select Soax Steps')
        self.getForm('SOAX_STEPS_SELECT').configure()
        self.setNextForm('SOAX_STEPS_SELECT')


    def soaxStepsSelectDone(self,
        do_auto_contrast,
        do_rescale,
        do_section,
        do_create_soax_params,
        do_run_soax,
        do_snakes_to_json,
        do_join_sectioned_snakes,
        do_scale_json_snakes_to_units,
        do_make_orientation_fields,
        ):
        self.do_auto_contrast = do_auto_contrast
        self.do_rescale = do_rescale
        self.do_section = do_section
        self.do_create_soax_params = do_create_soax_params
        self.do_run_soax = do_run_soax
        self.do_snakes_to_json = do_snakes_to_json
        self.do_join_sectioned_snakes = do_join_sectioned_snakes
        self.do_scale_json_snakes_to_units = do_scale_json_snakes_to_units
        self.do_make_orientation_fields = do_make_orientation_fields

        if self.do_auto_contrast:
            self.menu_functions.append(self.startAutoContrastSetup)
        if self.do_rescale:
            self.menu_functions.append(self.startRescaleSetup)
        if self.do_section:
            self.menu_functions.append(self.startSectioningSetup)
        if self.do_create_soax_params:
            self.menu_functions.append(self.startSoaxParamsSetupPage1)
            self.menu_functions.append(self.startSoaxParamsSetupPage2)
        if self.do_run_soax:
            self.menu_functions.append(self.startSoaxRunSetup)
        if self.do_snakes_to_json:
            self.menu_functions.append(self.startSnakesToJsonSetup)
        if self.do_join_sectioned_snakes:
            self.menu_functions.append(self.startJoinSectionedSnakesSetup)
        if self.do_scale_json_snakes_to_units:
            self.menu_functions.append(self.startScaleJsonSnakesToUnitsSetup)
        if self.do_make_orientation_fields:
            self.menu_functions.append(self.startMakeOrientationFieldsSetup)
        # if self.do_make_sindy_matrices_from_snakes:
        #     self.menu_functions.append(self.startMakeSindyMatricesFromSnakesSetup)

        # Move onto next index
        self.goToNextMenu()

    def startPIVStepsSelect(self):
        self.addForm('PIV_STEPS_SELECT', PIVStepsSelectForm, name='Select PIV Steps')
        self.getForm('PIV_STEPS_SELECT').configure()
        self.setNextForm('PIV_STEPS_SELECT')

    def PIVStepsSelectDone(self,
        do_bead_piv_auto_contrast,
        do_tube_piv_auto_contrast,
        do_bead_PIV,
        do_tube_PIV,
        ):
        self.do_bead_piv_auto_contrast = do_bead_piv_auto_contrast
        self.do_tube_piv_auto_contrast = do_tube_piv_auto_contrast
        self.do_bead_PIV = do_bead_PIV
        self.do_tube_PIV = do_tube_PIV

        if self.do_bead_piv_auto_contrast:
            self.menu_functions.append(self.startBeadPivAutoContrastSetup)
        if self.do_tube_piv_auto_contrast:
            self.menu_functions.append(self.startTubePivAutoContrastSetup)
        if self.do_bead_PIV:
            self.menu_functions.append(self.startBeadPIVSetup)
        if self.do_tube_PIV:
            self.menu_functions.append(self.startTubePIVSetup)

        self.goToNextMenu()

    def startAutoContrastSetup(self):
        self.addForm('AUTO_CONTRAST_SETUP', AutoContrastSetupForm, name='Auto Contrasting Setup')
        self.getForm('AUTO_CONTRAST_SETUP').configure(self.auto_contrast_settings, self.make_dirs)
        self.setNextForm('AUTO_CONTRAST_SETUP')

    def autoContrastSetupDone(self, auto_contrast_settings):
        self.auto_contrast_settings = auto_contrast_settings
        self.rescale_settings["source_tiff_dir"] = auto_contrast_settings["target_tiff_dir"]
        self.sectioning_settings["source_tiff_dir"] = auto_contrast_settings["target_tiff_dir"]
        self.soax_run_settings["source_tiff_dir"] = auto_contrast_settings["target_tiff_dir"]
        # If input TIFFs have been rescaled to range from 0 to 65535,
        # When SOAX runs and converts to floats, intensities should be rescaled from 0 to 1.0
        # We can't have 0.0 to 1.0 scale in original TIFFs because TIFFs have only integer brightness
        # levels
        img_search_depth = 0
        tif_max_level = self.get_first_tif_data_type_max(
            auto_contrast_settings["source_tiff_dir"],
            img_search_depth,
        )
        if tif_max_level is None:
            npyscreen.notify_confirm(
                "In soax run stage intensity_scaling will need to be set manually, could not find TIFF files in {} at depth {} to set intensity to 1 / tiff data type max value".format(auto_contrast_settings["source_tiff_dir"], img_search_depth),
                wide=True,
                editw=1)
        else:
            self.soax_params_page2_settings["intensity_scaling"] = format(1/tif_max_level, '.9f')

        self.goToNextMenu()

    def startRescaleSetup(self):
        self.addForm('RESCALE_SETUP', RescaleSetupForm, name='Rescale Setup')
        self.getForm('RESCALE_SETUP').configure(self.rescale_settings, self.make_dirs)
        self.setNextForm('RESCALE_SETUP')

    def RescaleSetupDone(self, rescale_settings):
        self.rescale_settings = rescale_settings

        self.sectioning_settings["source_tiff_dir"] = rescale_settings["target_tiff_dir"]
        self.soax_run_settings["source_tiff_dir"] = rescale_settings["target_tiff_dir"]

        self.goToNextMenu()

    def startSectioningSetup(self):
        self.addForm('SECTIONING_SETUP', SectioningSetupForm, name='Sectioning Setup')
        self.getForm('SECTIONING_SETUP').configure(self.sectioning_settings, self.make_dirs)
        self.setNextForm('SECTIONING_SETUP')

    def sectioningSetupDone(self, sectioning_settings):
        self.sectioning_settings = sectioning_settings
        self.soax_run_settings["source_tiff_dir"] = sectioning_settings["target_sectioned_tiff_dir"]
        self.soax_run_settings["use_subdirs"] = "yes"

        self.goToNextMenu()

    def startSoaxParamsSetupPage1(self):
        self.addForm('PARAM_SETUP_PAGE_1', SoaxParamsSetupPage1Form, name="SOAX Params Setup Page 1/2")
        self.getForm('PARAM_SETUP_PAGE_1').configure(self.soax_params_page1_settings, self.make_dirs)
        self.setNextForm('PARAM_SETUP_PAGE_1')

    def soaxParamsSetupPage1Done(self, soax_params_page1_settings):
        self.params_page1_settings = soax_params_page1_settings
        self.soax_run_settings["param_files_dir"] = soax_params_page1_settings["params_save_dir"]
        self.goToNextMenu()

    def startSoaxParamsSetupPage2(self):
        self.addForm('PARAM_SETUP_PAGE_2', SoaxParamsSetupPage2Form, name="SOAX Params Setup Page 2/2")
        self.getForm('PARAM_SETUP_PAGE_2').configure(self.soax_params_page2_settings, self.make_dirs)
        self.setNextForm('PARAM_SETUP_PAGE_2')

    def soaxParamsSetupPage2Done(self, soax_params_page2_settings):
        self.soax_params_page2_settings = soax_params_page2_settings
        self.goToNextMenu()

    def startSoaxRunSetup(self):
        self.addForm('SOAX_RUN_SETUP', SoaxRunSetupForm, name="SOAX Run Setup")
        self.getForm('SOAX_RUN_SETUP').configure(self.soax_run_settings, self.make_dirs)
        self.setNextForm('SOAX_RUN_SETUP')

    def soaxRunSetupDone(self, soax_run_settings):
        self.soax_run_settings = soax_run_settings
        self.snakes_to_json_settings["source_snakes_dir"] = soax_run_settings["target_snakes_dir"]

        if soax_run_settings["use_subdirs"] == "yes":
            self.snakes_to_json_settings["source_snakes_depth"] = "2"
        else:
            self.snakes_to_json_settings["source_snakes_depth"] = "1"

        # Only want to do this if we know soax is getting the original shaped images
        # if self.make_snake_images_settings["width"] == "" and not soax_run_settings["use_subdirs"]:
        #     # Set width and height for make images step
        #     img_depth = 0
        #     self.auto_set_width_height_images_settings(
        #         soax_run_settings["source_tiff_dir"],
        #         img_depth)

        # if self.make_snake_images_settings["background_images_dir"] == "":
        #     self.make_snake_images_settings["background_images_dir"] = soax_run_settings["source_tiff_dir"]

        self.goToNextMenu()

    def startSnakesToJsonSetup(self):
        self.addForm('SNAKES_TO_JSON_SETUP', SnakesToJsonSetupForm, name="Snakes to JSON Setup")
        self.getForm('SNAKES_TO_JSON_SETUP').configure(self.snakes_to_json_settings, self.make_dirs)
        self.setNextForm('SNAKES_TO_JSON_SETUP')

    def snakesToJsonSetupDone(self, snakes_to_json_settings):
        self.snakes_to_json_settings = snakes_to_json_settings

        target_json_dir = snakes_to_json_settings["target_json_dir"]
        self.join_sectioned_snakes_settings["source_json_dir"] = target_json_dir
        # self.make_snake_images_settings["source_json_dir"] = target_json_dir
        self.make_orientation_fields_settings["source_json_dir"] = target_json_dir
        # self.make_sindy_matrices_from_snakes_settings["source_json_dir"] = target_json_dir
        self.scale_json_snakes_to_units_settings["source_json_dir"] = target_json_dir

        output_jsons_depth = snakes_to_json_settings["source_snakes_depth"]
        self.join_sectioned_snakes_settings["source_jsons_depth"] = output_jsons_depth
        # self.make_snake_images_settings["source_jsons_depth"] = output_jsons_depth
        self.make_orientation_fields_settings["source_json_dir"] = output_jsons_depth
        # self.make_sindy_matrices_from_snakes_settings["source_jsons_depth"] = output_jsons_depth
        self.scale_json_snakes_to_units_settings["source_jsons_depth"] = output_jsons_depth

        self.goToNextMenu()

    def startJoinSectionedSnakesSetup(self):
        self.addForm('JOIN_SECTIONED_SNAKES_SETUP', JoinSectionedSnakesSetupForm, name="Join Sectioned Snakes Setup")
        self.getForm('JOIN_SECTIONED_SNAKES_SETUP').configure(self.join_sectioned_snakes_settings, self.make_dirs)
        self.setNextForm('JOIN_SECTIONED_SNAKES_SETUP')

    def joinSectionedSnakesSetupDone(self, join_sectioned_snakes_settings):
        self.join_sectioned_snakes_settings = join_sectioned_snakes_settings

        target_json_dir = join_sectioned_snakes_settings["target_json_dir"]
        self.scale_json_snakes_to_units_settings["source_json_dir"] = target_json_dir
        # self.make_snake_images_settings["source_json_dir"] = target_json_dir
        self.make_orientation_fields_settings["source_json_dir"] = target_json_dir
        # self.make_sindy_matrices_from_snakes_settings["source_json_dir"] = target_json_dir

        # Output jsons are one directory less deep since they've been joined
        output_jsons_depth = str(int(join_sectioned_snakes_settings["source_jsons_depth"]) - 1)
        self.scale_json_snakes_to_units_settings["source_jsons_depth"] = output_jsons_depth
        # self.make_snake_images_settings["source_jsons_depth"] = output_jsons_depth
        self.make_orientation_fields_settings["source_json_dir"] = output_jsons_depth
        # self.make_sindy_matrices_from_snakes_settings["source_jsons_depth"] = output_jsons_depth

        self.goToNextMenu()

    def startScaleJsonSnakesToUnitsSetup(self):
        self.addForm('SCALE_JSON_SNAKES_TO_UNITS', ScaleJsonSnakesToUnitsSetupForm, name="Scale JSON Snakes to Units")
        self.getForm('SCALE_JSON_SNAKES_TO_UNITS').configure(self.scale_json_snakes_to_units_settings, self.make_dirs)
        self.setNextForm('SCALE_JSON_SNAKES_TO_UNITS')

    def scaleJsonSnakesToUnitsSetupDone(self, scale_json_snakes_to_units_settings):
        self.scale_json_snakes_to_units_settings = scale_json_snakes_to_units_settings

        target_json_dir = scale_json_snakes_to_units_settings["target_json_dir"]
        # self.make_snake_images_settings["source_json_dir"] = target_json_dir
        self.make_orientation_fields_settings["source_json_dir"] = target_json_dir
        # self.make_sindy_matrices_from_snakes_settings["source_json_dir"] = target_json_dir

        output_jsons_depth = self.scale_json_snakes_to_units_settings["source_jsons_depth"]
        # self.make_snake_images_settings["source_jsons_depth"] = output_jsons_depth
        self.make_orientation_fields_settings["source_json_dir"] = output_jsons_depth
        # self.make_sindy_matrices_from_snakes_settings["source_jsons_depth"] = output_jsons_depth


    def startMakeOrientationFieldsSetup(self):
        self.addForm('MAKE_ORIENTATION_FIELDS', MakeOrientationFieldsSetupForm, name="Make Orientation Fields Setup")
        self.getForm('MAKE_ORIENTATION_FIELDS').configure(self.make_orientation_fields_settings, self.make_dirs)
        self.setNextForm('MAKE_ORIENTATION_FIELDS')

    def makeOrientationFieldsSetupDone(self, make_orientation_fields_settings):
        self.make_orientation_fields_settings = make_orientation_fields_settings
        self.goToNextMenu()

    def startBeadPivAutoContrastSetup(self):
        self.addForm('BEAD_PIV_AUTO_CONTRAST_SETUP', BeadPivAutoContrastSetupForm, name="Bead PIV Auto Contrast")
        self.getForm('BEAD_PIV_AUTO_CONTRAST_SETUP').configure(self.bead_piv_auto_contrast_settings, self.make_dirs)
        self.setNextForm('BEAD_PIV_AUTO_CONTRAST_SETUP')

    def beadPivAutoContrastSetupDone(self, bead_piv_auto_contrast_settings):
        self.bead_piv_auto_contrast_settings = bead_piv_auto_contrast_settings

        self.bead_PIV_settings["source_tiff_dir"] = bead_piv_auto_contrast_settings["target_tiff_dir"]

        self.goToNextMenu()

    def startTubePivAutoContrastSetup(self):
        self.addForm('TUBE_PIV_AUTO_CONTRAST_SETUP', TubePivAutoContrastSetupForm, name="Tube PIV Auto Contrast")
        self.getForm('TUBE_PIV_AUTO_CONTRAST_SETUP').configure(self.tube_piv_auto_contrast_settings, self.make_dirs)
        self.setNextForm('TUBE_PIV_AUTO_CONTRAST_SETUP')

    def tubePivAutoContrastSetupDone(self, tube_piv_auto_contrast_settings):
        self.tube_piv_auto_contrast_settings = tube_piv_auto_contrast_settings

        self.tube_PIV_settings["source_tiff_dir"] = tube_piv_auto_contrast_settings["target_tiff_dir"]

        self.goToNextMenu()

    def startBeadPIVSetup(self):
        self.addForm('BEAD_PIV_SETUP', BeadPIVSetupForm, name="Bead PIV Setup")
        self.getForm('BEAD_PIV_SETUP').configure(self.bead_PIV_settings, self.make_dirs)
        self.setNextForm('BEAD_PIV_SETUP')

    def beadPIVSetupDone(self, bead_PIV_settings):
        self.bead_PIV_settings = bead_PIV_settings
        self.goToNextMenu()

    def startTubePIVSetup(self):
        self.addForm('TUBE_PIV_SETUP', TubePIVSetupForm, name="Tube PIV Setup")
        self.getForm('TUBE_PIV_SETUP').configure(self.tube_PIV_settings, self.make_dirs)
        self.setNextForm('TUBE_PIV_SETUP')

    def tubePIVSetupDone(self, tube_PIV_settings):
        self.tube_PIV_settings = tube_PIV_settings
        self.goToNextMenu()
