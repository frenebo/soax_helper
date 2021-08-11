from create_param_files import error_string_or_parse_arg_or_range, create_param_files
import npyscreen
import os
from tiff_info import get_single_tiff_info
from snakeutils.files import find_files_or_folders_at_depth

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
                raise ParseException("'{}' does not exist".format(dir_string))

def check_file_field(field_name, file_path):
    if file_path == "":
        raise ParseException("'{}' is a required field".format(field_name))
    if not os.path.exists(file_path):
        raise ParseException("'{}' does not exist".format(file_path))
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


class StepsSetupForm(npyscreen.Form):
    def configure(self):
        self.select_steps = self.add(
            npyscreen.TitleMultiSelect,
            max_height =-2,
            value = [4,5,6,8,9],
            name="Pick steps (spacebar to toggle)",
            values = [
                "Auto Contrast Raw TIFFs",
                "Rescale TIFFs in Z",
                "Rescale TIFFs in X and Y",
                "Section TIFFs before running SOAX",
                "Create Parameter Files",
                "Run SOAX",
                "Convert Snake files to JSON",
                "Join Sectioned Snakes together (you should do this if input images to soax are sectioned)",
                "Make images of snakes",
                "Make videos from snake images",
                "Make Orientation Fields",
            ],
            scroll_exit=True,
        )

    def afterEditing(self):
        do_auto_contrast           = 0 in self.select_steps.value
        do_z_rescale               = 1 in self.select_steps.value
        do_xy_rescale              = 2 in self.select_steps.value
        do_section                 = 3 in self.select_steps.value
        do_create_params           = 4 in self.select_steps.value
        do_run_soax                = 5 in self.select_steps.value
        do_snakes_to_json          = 6 in self.select_steps.value
        do_join_sectioned_snakes   = 7 in self.select_steps.value
        do_make_snake_images       = 8 in self.select_steps.value
        do_make_snake_videos       = 9 in self.select_steps.value
        do_make_orientation_fields = 10 in self.select_steps.value

        self.parentApp.stagesSelected(
            do_auto_contrast,
            do_z_rescale,
            do_xy_rescale,
            do_section,
            do_create_params,
            do_run_soax,
            do_snakes_to_json,
            do_join_sectioned_snakes,
            do_make_snake_images,
            do_make_snake_videos,
            do_make_orientation_fields
        )

class SetupForm(npyscreen.Form):
    dir_fields = []
    file_fields = []
    pos_float_fields = []
    percentage_fields = []
    non_neg_int_fields = []
    pos_int_fields = []
    arg_or_range_fields = []
    file_fields = []
    optional_dir_fields = []
    yes_no_fields = []

    @classmethod
    def parseSettings(cls, field_strings, make_dirs_if_not_present=False):
        parsed_fields = {}

        for field_name in cls.dir_fields:
            field_str = field_strings[field_name]
            check_dir_field(field_name, field_str, make_dirs_if_not_present)
            parsed_fields[field_name] = field_str

        for field_name in cls.file_fields:
            field_str = field_strings[field_name]
            check_file_field(field_name, field_str)
            parsed_fields[field_name] = field_str

        for field_name in cls.pos_float_fields:
            field_str = field_strings[field_name]
            parsed_fields[field_name] = parse_pos_float(field_name, field_str)

        for field_name in cls.percentage_fields:
            field_str = field_strings[field_name]

            if field_str == "":
                raise ParseException("'{}' is a required field".format(field_name))
            try:
                perc = float(field_str)
            except ValueError:
                raise ParseException("'{}' value '{}' is not a number".format(field_name,field_str))


            if perc < 0 or perc > 100:
                raise ParseException("Invalid '{}' value '{}': should be between 0 and 100".format(field_name,str(perc)))

            parsed_fields[field_name] = perc

        for field_name in cls.pos_int_fields:
            field_str = field_strings[field_name]
            parsed_fields[field_name] = parse_pos_int(field_name, field_str)

        for field_name in cls.non_neg_int_fields:
            field_str = field_strings[field_name]
            parsed_fields[field_name] = parse_non_neg_int(field_name, field_str)

        for field_name in cls.arg_or_range_fields:
            field_str = field_strings[field_name]

            if field_str == "":
                raise ParseException("'{}' is a required field")

            err_str_or_val = error_string_or_parse_arg_or_range(field_str)
            if isinstance(err_str_or_val, str):
                raise ParseException("Error parsing {}: {}".format(field_name, err_str_or_val))
            else:
                parsed_fields[field_name] = err_str_or_val

        for field_name in cls.optional_dir_fields:
            field_str = field_strings[field_name]

            if field_str.strip() == "":
                parsed_fields[field_name] = None
            else:
                check_dir_field(field_name, field_str, make_dirs_if_not_present)
                parsed_fields[field_name] = field_str

        for field_name in cls.yes_no_fields:
            field_str = field_strings[field_name]
            parsed_fields[field_name] = True if field_str == "yes" else False

        return parsed_fields

    def __init__(self, *args, **kwargs):
        # Should be set in configure of form classes
        self.setup_done_func = None

        super(SetupForm, self).__init__(*args, **kwargs)

    def configure(self, settings):
        raise NotImplementedError()

    def getFieldStrings(self):
        raise NotImplementedError()

    def afterEditing(self):
        if hasattr(self, "create_if_not_present"):
            # option zero is "yes"
            make_dirs_if_not_present = 0 in self.create_if_not_present.value
        else:
            make_dirs_if_not_present = False

        try:
            self.parseSettings(self.getFieldStrings(), make_dirs_if_not_present)
        except ParseException as e:
            npyscreen.notify_confirm(str(e),editw=1)
            return
        if self.setup_done_func is None:
            raise Exception("Missing setup_done_func to call with argument strings")

        self.setup_done_func(self.getFieldStrings())

class ZRescaleSetupForm(SetupForm):
    dir_fields = ["source_tiff_dir", "target_tiff_dir"]
    pos_float_fields = ["rescale_factor"]
    file_fields = ["batch_resample_path"]

    def configure(self, z_rescale_settings):
        self.setup_done_func = self.parentApp.ZRescaleSetupDone

        self.add(npyscreen.FixedText,
            value="Rescale z-axis depth of images using SOAX batch_resample. Useful if making images smaller or correcting for z-slice size")
        self.field_batch_resample_path = self.add(npyscreen.TitleFilename, name="batch_resample_path",
            value=z_rescale_settings["batch_resample_path"])
        self.field_source_tiff_dir = self.add(npyscreen.TitleFilename, name="source_tiff_dir",
            value=z_rescale_settings["source_tiff_dir"])
        self.field_target_tiff_dir = self.add(npyscreen.TitleFilename, name="target_tiff_dir",
            value=z_rescale_settings["target_tiff_dir"])
        self.field_rescale_factor = self.add(npyscreen.TitleText, name="rescale_factor",
            value=z_rescale_settings["rescale_factor"])
        self.create_if_not_present = self.add(
            npyscreen.TitleSelectOne,
            name="Create dirs if not present",
            values=["yes", "no"],
            value=[1],
            scroll_exit=True)

    def getFieldStrings(self):
        return {
            "batch_resample_path": self.field_batch_resample_path.value,
            "source_tiff_dir": self.field_source_tiff_dir.value,
            "target_tiff_dir": self.field_target_tiff_dir.value,
            "rescale_factor": self.field_rescale_factor.value,
        }

class XYRescaleSetupForm(SetupForm):
    dir_fields = ["source_tiff_dir", "target_tiff_dir"]
    pos_float_fields = ["rescale_factor"]

    def configure(self, xy_rescale_settings):
        self.setup_done_func = self.parentApp.XYRescaleSetupDone
        self.add(npyscreen.FixedText,
            value="Rescale x and y width/height of images in source directory by factor (depth dimension unaffected for 3D images)")
        self.add(npyscreen.FixedText,
            value="Ex. rescale factor 0.5 would make images half as tall and wide")
        self.field_source_tiff_dir = self.add(npyscreen.TitleFilename, name="source_tiff_dir",
            value=xy_rescale_settings["source_tiff_dir"])
        self.field_target_tiff_dir = self.add(npyscreen.TitleFilename, name="target_tiff_dir",
            value=xy_rescale_settings["target_tiff_dir"])
        self.field_rescale_factor = self.add(npyscreen.TitleText, name="rescale_factor",
            value=xy_rescale_settings["rescale_factor"])
        self.create_if_not_present = self.add(
            npyscreen.TitleSelectOne,
            name="Create dirs if not present",
            values=["yes", "no"],
            value=[1],
            scroll_exit=True)

    def getFieldStrings(self):
        return {
            "source_tiff_dir": self.field_source_tiff_dir.value,
            "target_tiff_dir": self.field_target_tiff_dir.value,
            "rescale_factor": self.field_rescale_factor.value,
        }

class AutoConstrastSetupForm(SetupForm):
    percentage_fields = ["min_cutoff_percent", "max_cutoff_percent"]
    dir_fields = ["source_tiff_dir", "target_tiff_dir"]

    def configure(self, auto_contrast_settings):
        self.setup_done_func = self.parentApp.autoContrastSetupDone

        self.field_source_tiff_dir = self.add(npyscreen.TitleFilename, name="source_tiff_dir",
            value=auto_contrast_settings["source_tiff_dir"])
        self.field_target_tiff_dir = self.add(npyscreen.TitleFilename, name="target_tiff_dir",
            value=auto_contrast_settings["target_tiff_dir"])

        self.field_min_cutoff_percent = self.add(
            npyscreen.TitleText,
            value=auto_contrast_settings["min_cutoff_percent"],
            name="min_cutoff_percent")
        self.field_max_cutoff_percent = self.add(
            npyscreen.TitleText,
            value=auto_contrast_settings["max_cutoff_percent"],
            name="max_cutoff_percent")
        self.create_if_not_present = self.add(
            npyscreen.TitleSelectOne,
            name="Create dirs if not present",
            values=["yes", "no"],
            value=[1],
            scroll_exit=True)

        npyscreen.notify_confirm(
            "Min and max cutoff percent are brightness level percentiles to use to rescale the TIFF image brightnesses " +
            "min=1 and max=99 would find the brightness that only 1% of tiff pixels in the first TIF in the directory are dimmer than, " +
            "and the brightness that 99% of tiff pixels are dimmer than. The 1% brightness is the lower threshold, and 99% brightness is the upper threhold. " +
            "All pixels dimmer than the lower threshold are set to total black, all pixels brighter than the upper threshold are set to pure white, " +
            "and pixel brightnesses in between are rescaled to a new value between total black and total white",
            wide=True,
            editw=1,
        )

    def getFieldStrings(self):
        return {
            "max_cutoff_percent": self.field_max_cutoff_percent.value,
            "min_cutoff_percent": self.field_min_cutoff_percent.value,
            "source_tiff_dir": self.field_source_tiff_dir.value,
            "target_tiff_dir": self.field_target_tiff_dir.value,
        }

class SectioningSetupForm(SetupForm):
    pos_int_fields = ["section_max_size"]
    dir_fields = ["source_tiff_dir", "target_sectioned_tiff_dir"]

    def configure(self, sectioning_settings):
        self.setup_done_func = self.parentApp.sectioningSetupDone

        self.field_source_dir = self.add(npyscreen.TitleFilename, name="source_tiff_dir",
            value=sectioning_settings["source_tiff_dir"])
        self.field_sectioned_target_dir = self.add(npyscreen.TitleFilename, name="target_sectioned_tiff_dir",
            value=sectioning_settings["target_sectioned_tiff_dir"])

        self.add(npyscreen.FixedText, value="Enter maximum side length (pixels) of an image section")

        self.field_section_max_size = self.add(npyscreen.TitleText, name="section max size",
            value=sectioning_settings["section_max_size"])

        self.create_if_not_present = self.add(
            npyscreen.TitleSelectOne,
            name="Create dirs if not present",
            values=["yes", "no"],
            value=[1],
            scroll_exit=True)

    def getFieldStrings(self):
        return {
            "source_tiff_dir": self.field_source_dir.value,
            "target_sectioned_tiff_dir": self.field_sectioned_target_dir.value,
            "section_max_size": self.field_section_max_size.value,
        }

class ParamsSetupPage1Form(SetupForm):
    dir_fields = ["params_save_dir"]
    arg_or_range_fields = [
        "alpha",
        "beta",
        "gamma",
        "min_foreground",
        "ridge_threshold",
        "min_snake_length",
    ]

    all_fields = dir_fields + arg_or_range_fields

    def configure(self, params_page1_settings):
        self.setup_done_func = self.parentApp.paramsSetupPage1Done
        self.add(npyscreen.FixedText,
            value="Enter SOAX run parameters to try.")
        self.add(npyscreen.FixedText,
            value="Enter number values (ex. 1,3.44,10.3) or start-stop-step ranges (ex. 1-20-0.5,1.5-3.5-1.0)")
        self.add(npyscreen.FixedText,
            value="If ranges are given, soax will be run multiple times, trying all combinations of parameter values")

        self.field_params_save_dir = self.add(npyscreen.TitleFilename, name="params_save_dir",
            value=params_page1_settings["params_save_dir"])

        self.field_alpha           = self.add(npyscreen.TitleText, name="alpha",
            value=params_page1_settings["alpha"])
        self.field_beta            = self.add(npyscreen.TitleText, name="beta",
            value=params_page1_settings["beta"])
        self.field_gamma            = self.add(npyscreen.TitleText, name="gamma",
            value=params_page1_settings["gamma"])
        self.field_min_foreground  = self.add(npyscreen.TitleText, name="min_foreground",
            value=params_page1_settings["min_foreground"])
        self.field_ridge_threshold = self.add(npyscreen.TitleText, name="ridge_threshold",
            value=params_page1_settings["ridge_threshold"])
        self.field_min_snake_length = self.add(npyscreen.TitleText, name="min_snake_length",
            value=params_page1_settings["min_snake_length"])

        self.create_if_not_present = self.add(
            npyscreen.TitleSelectOne,
            name="Create dirs if not present",
            values=["yes", "no"],
            value=[1],
            scroll_exit=True)

    def getFieldStrings(self):
        return {
            "params_save_dir": self.field_params_save_dir.value,
            "alpha": self.field_alpha.value,
            "beta": self.field_beta.value,
            "gamma": self.field_gamma.value,
            "min_foreground": self.field_min_foreground.value,
            "ridge_threshold": self.field_ridge_threshold.value,
            "min_snake_length": self.field_min_snake_length.value,
        }

class ParamsSetupPage2Form(SetupForm):
    dir_fields = []
    arg_or_range_fields = [
        "gaussian_std",
        "snake_point_spacing",
        "external_factor",
        "intensity_scaling",
    ]
    all_fields = dir_fields + arg_or_range_fields

    def configure(self, params_page2_settings):
        self.setup_done_func = self.parentApp.paramsSetupPage2Done

        self.field_gaussian_std = self.add(npyscreen.TitleText, name="gaussian_std",
            value=params_page2_settings["gaussian_std"])
        self.field_snake_point_spacing = self.add(npyscreen.TitleText, name="snake_point_spacing",
            value=params_page2_settings["snake_point_spacing"])
        self.field_external_factor = self.add(npyscreen.TitleText, name="external_factor",
            value=params_page2_settings["external_factor"])
        self.add(npyscreen.FixedText,
            value="Intensity scaling controls how SOAX rescales image brightness. 0=automatic rescaling")
        self.add(npyscreen.FixedText,
            value="If input images have been contrast-scaled in a previous step, we don't want SOAX to rescale brightness")
        self.add(npyscreen.FixedText,
            value="In this case, set intensity_scaling to 1/65535 = 0.000015259. to rescale from TIF max intensity to 1.0 max intensity")
        self.add(npyscreen.FixedText,
            value="If input images are sectioned before feeding to SOAX, they should be contrast rescaled")
        self.add(npyscreen.FixedText,
            value="before sectioning, so all sections have same contrast setting")
        self.field_intensity_scaling = self.add(npyscreen.TitleText, name="intensity_scaling",
            value=params_page2_settings["intensity_scaling"])

    def getFieldStrings(self):
        return {
            "gaussian_std": self.field_gaussian_std.value,
            "snake_point_spacing": self.field_snake_point_spacing.value,
            "external_factor": self.field_external_factor.value,
            "intensity_scaling": self.field_intensity_scaling.value,
        }

class ParamsSetupForm(SetupForm):
    dir_fields = ParamsSetupPage1Form.dir_fields + ParamsSetupPage2Form.dir_fields
    arg_or_range_fields = ParamsSetupPage1Form.arg_or_range_fields + ParamsSetupPage2Form.arg_or_range_fields

    def configure(self):
        raise Exception("Only exists for parse stuff")

class SoaxRunSetupForm(SetupForm):
    dir_fields = [
        "source_tiff_dir",
        "target_snakes_dir",
        "param_files_dir",
        "soax_log_dir",
    ]

    file_fields = ["batch_soax_path"]
    pos_int_fields = ["workers"]
    yes_no_fields = ["use_subdirs"]

    def configure(self, soax_run_settings):
        self.setup_done_func = self.parentApp.soaxRunSetupDone
        self.add(npyscreen.FixedText,
            value="note: workers field is number of batch_soax instances to run at once")

        self.field_source_dir = self.add(npyscreen.TitleFilename, name="source_tiff_dir",
            value=soax_run_settings["source_tiff_dir"])
        self.field_target_snakes = self.add(npyscreen.TitleFilename, name="target_snakes_dir",
            value=soax_run_settings["target_snakes_dir"])
        self.field_param_files_dir = self.add(npyscreen.TitleFilename, name="param_files_dir",
            value=soax_run_settings["param_files_dir"])
        self.field_soax_log_dir = self.add(npyscreen.TitleFilename, name="soax_log_dir",
            value=soax_run_settings["soax_log_dir"])
        self.field_soax_executable_path = self.add(npyscreen.TitleFilename, name="batch_soax_path",
            value=soax_run_settings["batch_soax_path"])
        self.field_worker_number = self.add(npyscreen.TitleFilename, name="workers",
            value=soax_run_settings["workers"])

        self.create_if_not_present = self.add(
            npyscreen.TitleSelectOne,
            max_height = 3,
            name="Create dirs if not present",
            values=["yes", "no"],
            value=[1],
            scroll_exit=True)

        self.use_subdirs = self.add(
            npyscreen.TitleSelectOne,
            max_height = 3,
            name="Expect source images to be in subdirs (should be true if images are sectioned)",
            values=["yes", "no"],
            value=([0] if soax_run_settings["use_subdirs"] == "yes" else [1]),
            scroll_exit=True)

    def getFieldStrings(self):
        return {
            "use_subdirs": "yes" if (0 in self.use_subdirs.value) else "no",

            "source_tiff_dir": self.field_source_dir.value,
            "target_snakes_dir": self.field_target_snakes.value,
            "param_files_dir": self.field_param_files_dir.value,
            "soax_log_dir": self.field_soax_log_dir.value,

            "batch_soax_path": self.field_soax_executable_path.value,
            "workers": self.field_worker_number.value,
        }

class SnakesToJsonSetupForm(SetupForm):
    non_neg_int_fields = ["subdir_depth"]
    dir_fields = ["source_snakes_dir", "target_json_dir"]

    def configure(self, snakes_to_json_settings):
        self.setup_done_func = self.parentApp.snakesToJsonSetupDone
        self.add(npyscreen.FixedText,
            value="Convert snakes from the SOAX's text output to JSON.")

        self.field_source_snakes_dir = self.add(npyscreen.TitleFilename, name="source_snakes_dir",
            value=snakes_to_json_settings["source_snakes_dir"])
        self.field_target_json_dir = self.add(npyscreen.TitleFilename, name="target_json_dir",
            value=snakes_to_json_settings["target_json_dir"])

        self.field_subdir_depth = self.add(npyscreen.TitleText, name="subdir_depth",
            value=snakes_to_json_settings["subdir_depth"])

        self.create_if_not_present = self.add(
            npyscreen.TitleSelectOne,
            name="Create dirs if not present",
            values=["yes", "no"],
            value=[1],
            scroll_exit=True)

    def getFieldStrings(self):
        return {
            "source_snakes_dir": self.field_source_snakes_dir.value,
            "target_json_dir": self.field_target_json_dir.value,
            "subdir_depth": self.field_subdir_depth.value,
        }

class JoinSectionedSnakesSetupForm(SetupForm):
    non_neg_int_fields = ["source_jsons_depth"]
    dir_fields = ["source_json_dir", "target_json_dir"]

    def configure(self, join_sectioned_snakes_settings):
        self.setup_done_func = self.parentApp.joinSectionedSnakesSetupDone

        self.add(npyscreen.FixedText,
            value="Join JSON snake files from sections of an image")
        self.add(npyscreen.FixedText,
            value="to form JSON files with all the snakes from original images")

        self.field_source_json_dir = self.add(npyscreen.TitleFilename, name="source_json_dir",
            value=join_sectioned_snakes_settings["source_json_dir"])
        self.field_target_json_dir = self.add(npyscreen.TitleFilename, name="target_json_dir",
            value=join_sectioned_snakes_settings["target_json_dir"])

        self.field_source_jsons_depth = self.add(npyscreen.TitleText, name="source_jsons_depth",
            value=join_sectioned_snakes_settings["source_jsons_depth"])

        self.create_if_not_present = self.add(
            npyscreen.TitleSelectOne,
            name="Create dirs if not present",
            values=["yes", "no"],
            value=[1],
            scroll_exit=True)

    def getFieldStrings(self):
        return {
            "source_json_dir": self.field_source_json_dir.value,
            "target_json_dir": self.field_target_json_dir.value,
            "source_jsons_depth": self.field_source_jsons_depth.value,
        }

class MakeSnakeImagesSetupForm(SetupForm):
    non_neg_int_fields = ["snake_files_depth"]
    pos_int_fields = ["height", "width"]
    dir_fields = ["source_json_dir", "target_jpeg_dir"]
    optional_dir_fields = ["background_images_dir"]
    yes_no_fields = ["use_colors"]

    def configure(self, make_snake_images_settings):
        self.setup_done_func = self.parentApp.makeSnakeImagesSetupDone

        self.add(npyscreen.FixedText,
            value="Make videos from images in directories")
        self.field_source_json_dir = self.add(npyscreen.TitleFilename, name="source_json_dir",
            value=make_snake_images_settings["source_json_dir"])
        self.field_target_jpeg_dir = self.add(npyscreen.TitleFilename, name="target_jpeg_dir",
            value=make_snake_images_settings["target_jpeg_dir"])
        self.field_background_images_dir = self.add(npyscreen.TitleFilename, name="(Optional) background_images_dir",
            value=make_snake_images_settings["background_images_dir"])

        self.field_snake_files_depth = self.add(npyscreen.TitleText, name="snake_files_depth",
            value=make_snake_images_settings["snake_files_depth"])

        self.field_height = self.add(npyscreen.TitleText, name="height",
            value=make_snake_images_settings["height"])
        self.field_width = self.add(npyscreen.TitleText, name="width",
            value=make_snake_images_settings["width"])

        self.field_use_colors = self.add(
            npyscreen.TitleSelectOne,
            max_height = 3,
            name="Graph snakes with different colors",
            values=["yes", "no"],
            value=([0] if make_snake_images_settings["use_colors"] == "yes" else [1]),
            scroll_exit=True)

        self.create_if_not_present = self.add(
            npyscreen.TitleSelectOne,
            name="Create dirs if not present",
            values=["yes", "no"],
            value=[1],
            scroll_exit=True)

    def getFieldStrings(self):
        return {
            "source_json_dir": self.field_source_json_dir.value,
            "target_jpeg_dir": self.field_target_jpeg_dir.value,
            "height": self.field_height.value,
            "width": self.field_width.value,
            "snake_files_depth": self.field_snake_files_depth.value,
            "use_colors": "yes" if (0 in self.field_use_colors.value) else "no",
            "background_images_dir": self.field_background_images_dir.value,
        }

class MakeSnakeVideosSetupForm(SetupForm):
    dir_fields = ["source_jpeg_dir", "target_mp4_dir"]
    non_neg_int_fields = ["source_images_depth"]

    def configure(self, make_snake_videos_settings):
        self.setup_done_func = self.parentApp.makeSnakeVideosSetupDone
        self.add(npyscreen.FixedText,
            value="Make videos from images in directories")
        self.field_source_jpeg_dir = self.add(npyscreen.TitleFilename, name="source_jpeg_dir",
            value=make_snake_videos_settings["source_jpeg_dir"])
        self.field_target_mp4_dir = self.add(npyscreen.TitleFilename, name="target_mp4_dir",
            value=make_snake_videos_settings["target_mp4_dir"])

        self.field_source_images_depth = self.add(npyscreen.TitleText, name="source_images_depth",
            value=make_snake_videos_settings["source_images_depth"])

        self.create_if_not_present = self.add(
            npyscreen.TitleSelectOne,
            max_height=3,
            name="Create dirs if not present",
            values=["yes", "no"],
            value=[1],
            scroll_exit=True)

    def getFieldStrings(self):
        return {
            "source_jpeg_dir": self.field_source_jpeg_dir.value,
            "target_mp4_dir": self.field_target_mp4_dir.value,
            "source_images_depth": self.field_source_images_depth.value,
        }

class MakeOrientationFieldsSetupForm(SetupForm):
    dir_fields = ["source_json_dir", "target_data_dir"]
    non_neg_int_fields = ["source_jsons_depth"]
    pos_int_fields = ["image_width", "image_height"]

    def configure(self, make_orientation_fields_settings):
        self.setup_done_func = self.parentApp.makeOrientationFieldsSetupDone

        self.field_source_json_dir = self.add(npyscreen.TitleFilename, name="source_json_dir",
            value=make_orientation_fields_settings["source_json_dir"])
        self.field_target_data_dir = self.add(npyscreen.TitleFilename, name="target_data_dir",
            value=make_orientation_fields_settings["target_data_dir"])
        self.field_source_jsons_depth = self.add(npyscreen.TitleText, name="source_jsons_depth",
            value=make_orientation_fields_settings["source_jsons_depth"])
        self.field_image_width = self.add(npyscreen.TitleText, name="image_width",
            value=make_orientation_fields_settings["image_width"])
        self.field_image_height = self.add(npyscreen.TitleText, name="image_height",
            value=make_orientation_fields_settings["image_height"])

        self.create_if_not_present = self.add(
            npyscreen.TitleSelectOne,
            max_height=3,
            name="Create dirs if not present",
            values=["yes", "no"],
            value=[1],
            scroll_exit=True)

    def getFieldStrings(self):
        return {
            "source_json_dir": self.field_source_json_dir.value,
            "target_data_dir": self.field_target_data_dir.value,
            "source_jsons_depth": self.field_source_jsons_depth.value,
            "image_width": self.field_image_width.value,
            "image_height": self.field_image_height.value,
        }

class SoaxSetupApp(npyscreen.NPSAppManaged):
    def onStart(self):
        # Default settings to show in forms
        # Not all of these will necessarily be used if self.do_xy_rescale, self.do_auto_contrast, self.do_section, etc are False
        self.auto_contrast_settings = {
            "max_cutoff_percent": "95.5",
            "min_cutoff_percent": "0.1",
            "source_tiff_dir": "",
            "target_tiff_dir": "./AutoContrastedTIFFs",
        }
        self.z_rescale_settings = {
            "batch_resample_path": "/home/paul/Documents/build_soax_july3_follow_ubuntu_18_guide/build_soax/batch_resample",
            "source_tiff_dir": "",
            "target_tiff_dir": "./ZRescaledTIFFs",
            "rescale_factor": "1.0",
        }
        self.xy_rescale_settings = {
            "source_tiff_dir": "",
            "target_tiff_dir": "./XYRescaledTIFFs",
            "rescale_factor": "1.0",
        }
        self.sectioning_settings = {
            "source_tiff_dir": "",
            "target_sectioned_tiff_dir": "./SectionedTIFFs",
            "section_max_size": "200",
        }
        self.params_page1_settings = {
            "params_save_dir": "./Params",
            "alpha": "0.01",
            "beta": "0.1",
            "gamma": "2",
            "min_foreground":"10",
            "ridge_threshold":"0.01",
            "min_snake_length":"20",
        }
        self.params_page2_settings = {
            "gaussian_std":"0",
            "snake_point_spacing":"5",
            "external_factor":"1",
            "intensity_scaling": "0",
        }
        self.soax_run_settings = {
            "workers": "1",
            "use_subdirs": "no",
            "batch_soax_path": "/home/paul/Documents/build_soax_july3_follow_ubuntu_18_guide/build_soax/batch_soax",
            "source_tiff_dir": "",
            "target_snakes_dir": "./Snakes",
            "param_files_dir": "",
            "soax_log_dir": "./SoaxLogs",
        }
        self.snakes_to_json_settings = {
            "source_snakes_dir": "",
            "target_json_dir": "./JsonSnakes",
            "subdir_depth": "1",
        }
        self.join_sectioned_snakes_settings = {
            "source_json_dir": "",
            "target_json_dir": "./JoinedJsonSnakes",
            "source_jsons_depth": "2",
        }
        self.make_snake_images_settings = {
            "source_json_dir": "",
            "target_jpeg_dir": "./SnakeImages",
            "width": "",
            "height": "",
            "snake_files_depth": "1",
            "use_colors": "no",
            "background_images_dir": "",
        }
        self.make_snake_videos_settings = {
            "source_jpeg_dir": "",
            "target_mp4_dir": "./SnakeVideos",
            "source_images_depth": "1",
        }
        self.make_orientation_fields_settings = {
            "source_json_dir": "",
            "source_jsons_depth": "1",
            "target_data_dir": "./OrientationFields",
            "image_width": "",
            "image_height": "",
        }

        self.addForm('MAIN', StepsSetupForm, name='Select Steps')
        self.getForm('MAIN').configure()

    def getActionConfigs(self):
        action_configs = []
        if self.do_auto_contrast:
            action_configs.append({
                "action": "auto_contrast_tiffs",
                "settings": self.auto_contrast_settings,
            })
        if self.do_z_rescale:
            action_configs.append({
                "action": "z_rescale_tiffs",
                "settings": self.z_rescale_settings,
            })
        if self.do_xy_rescale:
            action_configs.append({
                "action": "xy_rescale_tiffs",
                "settings": self.xy_rescale_settings,
            })
        if self.do_section:
            action_configs.append({
                "action": "section_tiffs",
                "settings": self.sectioning_settings,
            })
        if self.do_create_params:
            action_configs.append({
                "action": "create_param_files",
                # Combine page 1 and page 2 settings
                "settings": {
                    **self.params_page1_settings,
                    **self.params_page2_settings,
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
        if self.do_make_snake_images:
            action_configs.append({
                "action": "make_snake_images",
                "settings": self.make_snake_images_settings,
            })
        if self.do_make_snake_videos:
            action_configs.append({
                "action": "make_videos",
                "settings": self.make_snake_videos_settings,
            })
        if self.do_make_orientation_fields:
            action_configs.append({
                "action": "make_orientation_fields",
                "settings": self.make_orientation_fields_settings,
            })
        return action_configs

    def stagesSelected(self,
        do_auto_contrast,
        do_z_rescale,
        do_xy_rescale,
        do_section,
        do_create_params,
        do_run_soax,
        do_snakes_to_json,
        do_join_sectioned_snakes,
        do_make_snake_images,
        do_make_snake_videos,
        do_make_orientation_fields,
        ):
        self.do_auto_contrast = do_auto_contrast
        self.do_z_rescale = do_z_rescale
        self.do_xy_rescale = do_xy_rescale
        self.do_section = do_section
        self.do_create_params = do_create_params
        self.do_run_soax = do_run_soax
        self.do_snakes_to_json = do_snakes_to_json
        self.do_join_sectioned_snakes = do_join_sectioned_snakes
        self.do_make_snake_images = do_make_snake_images
        self.do_make_snake_videos = do_make_snake_videos
        self.do_make_orientation_fields = do_make_orientation_fields

        self.menu_functions = []
        if self.do_auto_contrast:
            self.menu_functions.append(self.startAutoContrastSetup)
        if self.do_z_rescale:
            self.menu_functions.append(self.startZRescaleSetup)
        if self.do_xy_rescale:
            self.menu_functions.append(self.startXYRescaleSetup)
        if self.do_section:
            self.menu_functions.append(self.startSectioningSetup)
        if self.do_create_params:
            self.menu_functions.append(self.startParamSetupPage1)
            self.menu_functions.append(self.startParamSetupPage2)
        if self.do_run_soax:
            self.menu_functions.append(self.startSoaxRunSetup)
        if self.do_snakes_to_json:
            self.menu_functions.append(self.startSnakesToJsonSetup)
        if self.do_join_sectioned_snakes:
            self.menu_functions.append(self.startJoinSectionedSnakesSetup)
        if self.do_make_snake_images:
            self.menu_functions.append(self.startMakeSnakeImagesSetup)
        if self.do_make_snake_videos:
            self.menu_functions.append(self.startVideoSetup)
        if self.do_make_orientation_fields:
            self.menu_functions.append(self.startMakeOrientationFieldsSetup)

        self.form_index = -1
        # Move onto index 0
        self.goToNextMenu()

    def auto_set_width_height_images_settings(self, tiff_dir, img_depth, rescale_factor=None):
        image_locations_info = find_files_or_folders_at_depth(tiff_dir, img_depth, file_extensions=[".tiff", ".tif"])

        #If source tiff dir doesn't have anything at this depth, we won't do anything here
        if len(image_locations_info) == 0:
            return
        first_img_dir = image_locations_info[0][0]
        first_img_name = image_locations_info[0][1]
        first_img_fp = os.path.join(first_img_dir, first_img_name)
        shape, stack_height, dtype = get_single_tiff_info(first_img_fp)
        width, height = shape
        if rescale_factor is not None:
            width = int(width * rescale_factor)
            height = int(height * rescale_factor)
        self.make_snake_images_settings["width"] = str(width)
        self.make_snake_images_settings["height"] = str(height)

    def goToNextMenu(self):
        self.form_index += 1
        if self.form_index >= len(self.menu_functions):
            self.setNextForm(None)
        else:
            next_menu_func = self.menu_functions[self.form_index]
            next_menu_func()

    def startAutoContrastSetup(self):
        self.addForm('AUTO_CONTRAST_SETUP', AutoConstrastSetupForm, name='Auto Contrasting Setup')
        self.getForm('AUTO_CONTRAST_SETUP').configure(self.auto_contrast_settings)
        self.setNextForm('AUTO_CONTRAST_SETUP')

    def autoContrastSetupDone(self, auto_contrast_settings):
        self.auto_contrast_settings = auto_contrast_settings
        self.xy_rescale_settings["source_tiff_dir"] = auto_contrast_settings["target_tiff_dir"]
        self.z_rescale_settings["source_tiff_dir"] = auto_contrast_settings["target_tiff_dir"]
        self.sectioning_settings["source_tiff_dir"] = auto_contrast_settings["target_tiff_dir"]
        self.soax_run_settings["source_tiff_dir"] = auto_contrast_settings["target_tiff_dir"]
        # If input TIFFs have been rescaled to range from 0 to 65535,
        # When SOAX runs and converts to floats, intensities should be rescaled from 0 to 1.0
        # We can't have 0.0 to 1.0 scale in original TIFFs because TIFFs have only integer brightness
        # levels
        self.params_page2_settings["intensity_scaling"] = format(1/65535, '.9f')

        if self.make_snake_images_settings["width"] == "":
            self.auto_set_width_height_images_settings(
                auto_contrast_settings["source_tiff_dir"],
                0,
            )
        if self.make_snake_images_settings["background_images_dir"] == "":
            self.make_snake_images_settings["background_images_dir"] = auto_contrast_settings["target_tiff_dir"]

        self.goToNextMenu()

    def startZRescaleSetup(self):
        self.addForm('Z_RESCALE_SETUP', ZRescaleSetupForm, name='Z Rescale Setup')
        self.getForm('Z_RESCALE_SETUP').configure(self.z_rescale_settings)
        self.setNextForm('Z_RESCALE_SETUP')

    def ZRescaleSetupDone(self, z_rescale_settings):
        self.z_rescale_settings = z_rescale_settings
        self.xy_rescale_settings["source_tiff_dir"] = z_rescale_settings["target_tiff_dir"]
        # self.auto_contrast_settings["source_tiff_dir"] = z_rescale_settings["target_tiff_dir"]
        self.sectioning_settings["source_tiff_dir"] = z_rescale_settings["target_tiff_dir"]
        self.soax_run_settings["source_tiff_dir"] = z_rescale_settings["target_tiff_dir"]

        self.goToNextMenu()

    def startXYRescaleSetup(self):
        self.addForm('XY_RESCALE_SETUP', XYRescaleSetupForm, name='Rescale Setup')
        self.getForm('XY_RESCALE_SETUP').configure(self.xy_rescale_settings)
        self.setNextForm('XY_RESCALE_SETUP')

    def XYRescaleSetupDone(self, xy_rescale_settings):
        self.xy_rescale_settings = xy_rescale_settings

        # self.auto_contrast_settings["source_tiff_dir"] = xy_rescale_settings["target_tiff_dir"]
        self.sectioning_settings["source_tiff_dir"] = xy_rescale_settings["target_tiff_dir"]
        self.soax_run_settings["source_tiff_dir"] = xy_rescale_settings["target_tiff_dir"]
        if self.make_snake_images_settings["width"] == "":
            if self.do_z_rescale:
                img_source_dir = self.z_rescale_settings["source_tiff_dir"]
            else:
                img_source_dir = xy_rescale_settings["source_tiff_dir"]

            self.auto_set_width_height_images_settings(
                img_source_dir,
                0,
                rescale_factor=float(xy_rescale_settings["rescale_factor"]),
            )

        if self.make_snake_images_settings["background_images_dir"] == "":
            self.make_snake_images_settings["background_images_dir"] = xy_rescale_settings["target_tiff_dir"]

        self.goToNextMenu()

    def startSectioningSetup(self):
        self.addForm('SECTIONING_SETUP', SectioningSetupForm, name='Sectioning Setup')
        self.getForm('SECTIONING_SETUP').configure(self.sectioning_settings)
        self.setNextForm('SECTIONING_SETUP')

    def sectioningSetupDone(self, sectioning_settings):
        self.sectioning_settings = sectioning_settings
        self.soax_run_settings["source_tiff_dir"] = sectioning_settings["target_sectioned_tiff_dir"]
        self.soax_run_settings["use_subdirs"] = "yes"
        self.snakes_to_json_settings["subdir_depth"] = "2"
        self.join_sectioned_snakes_settings["source_jsons_depth"] = "2"
        if self.make_snake_images_settings["width"] == "":
            self.auto_set_width_height_images_settings(
                self.sectioning_settings["source_tiff_dir"],
                0,
            )
        self.goToNextMenu()

    def startParamSetupPage1(self):
        self.addForm('PARAM_SETUP_PAGE_1', ParamsSetupPage1Form, name="SOAX Params Setup Page 1/2")
        self.getForm('PARAM_SETUP_PAGE_1').configure(self.params_page1_settings)
        self.setNextForm('PARAM_SETUP_PAGE_1')

    def paramsSetupPage1Done(self, params_page1_settings):
        self.params_page1_settings = params_page1_settings
        self.soax_run_settings["param_files_dir"] = params_page1_settings["params_save_dir"]
        self.goToNextMenu()

    def startParamSetupPage2(self):
        self.addForm('PARAM_SETUP_PAGE_1', ParamsSetupPage2Form, name="SOAX Params Setup Page 2/2")
        self.getForm('PARAM_SETUP_PAGE_1').configure(self.params_page2_settings)
        self.setNextForm('PARAM_SETUP_PAGE_1')

    def paramsSetupPage2Done(self, params_page2_settings):
        self.params_page2_settings = params_page2_settings
        self.goToNextMenu()

    def startSoaxRunSetup(self):
        self.addForm('SOAX_RUN_SETUP', SoaxRunSetupForm, name="SOAX Run Setup")
        self.getForm('SOAX_RUN_SETUP').configure(self.soax_run_settings)
        self.setNextForm('SOAX_RUN_SETUP')

    def soaxRunSetupDone(self, soax_run_settings):
        self.soax_run_settings = soax_run_settings
        self.snakes_to_json_settings["source_snakes_dir"] = soax_run_settings["target_snakes_dir"]

        # Only want to do this if we know soax is getting the original shaped images
        if self.make_snake_images_settings["width"] == "" and not soax_run_settings["use_subdirs"]:
            # Set width and height for make images step
            img_depth = 0
            self.auto_set_width_height_images_settings(
                soax_run_settings["source_tiff_dir"],
                img_depth)

        if self.make_snake_images_settings["background_images_dir"] == "":
            self.make_snake_images_settings["background_images_dir"] = soax_run_settings["source_tiff_dir"]

        self.goToNextMenu()

    def startSnakesToJsonSetup(self):
        self.addForm('SNAKES_TO_JSON_SETUP', SnakesToJsonSetupForm, name="Snakes to JSON Setup")
        self.getForm('SNAKES_TO_JSON_SETUP').configure(self.snakes_to_json_settings)
        self.setNextForm('SNAKES_TO_JSON_SETUP')

    def snakesToJsonSetupDone(self, snakes_to_json_settings):
        self.snakes_to_json_settings = snakes_to_json_settings
        self.join_sectioned_snakes_settings["source_json_dir"] = snakes_to_json_settings["target_json_dir"]
        self.make_snake_images_settings["source_json_dir"] = snakes_to_json_settings["target_json_dir"]
        self.make_orientation_fields["source_json_dir"] = snakes_to_json_settings["target_json_dir"]
        self.goToNextMenu()

    def startJoinSectionedSnakesSetup(self):
        self.addForm('JOIN_SECTIONED_SNAKES_SETUP', JoinSectionedSnakesSetupForm, name="Join Sectioned Snakes Setup")
        self.getForm('JOIN_SECTIONED_SNAKES_SETUP').configure(self.join_sectioned_snakes_settings)
        self.setNextForm('JOIN_SECTIONED_SNAKES_SETUP')

    def joinSectionedSnakesSetupDone(self, join_sectioned_snakes_settings):
        self.join_sectioned_snakes_settings = join_sectioned_snakes_settings
        self.make_snake_images_settings["source_json_dir"] = join_sectioned_snakes_settings["target_json_dir"]
        self.make_orientation_fields["source_json_dir"] = join_sectioned_snakes_settings["target_json_dir"]
        # Output jsons are one directory less deep since they've been joined
        self.make_snake_images_settings["snake_files_depth"] = str(int(join_sectioned_snakes_settings["source_jsons_depth"]) - 1)
        self.goToNextMenu()

    def startMakeSnakeImagesSetup(self):
        self.addForm('MAKE_SNAKE_IMAGES_SETUP', MakeSnakeImagesSetupForm, name="Make Snake Images Setup")
        self.getForm('MAKE_SNAKE_IMAGES_SETUP').configure(self.make_snake_images_settings)
        self.setNextForm('MAKE_SNAKE_IMAGES_SETUP')

    def makeSnakeImagesSetupDone(self, make_snake_images_settings):
        self.make_snake_images_settings = make_snake_images_settings
        self.make_snake_videos_settings["source_jpeg_dir"] = make_snake_images_settings["target_jpeg_dir"]
        self.goToNextMenu()

    def startMakeOrientationFieldsSetup(self):
        self.addForm('MAKE_ORIENTATION_FIELDS', MakeOrientationFieldsSetupForm, name="Make Orientation Fields Setup")
        self.getForm('MAKE_ORIENTATION_FIELDS').configure(self.make_orientation_fields_settings)
        self.setNextForm('MAKE_ORIENTATION_FIELDS')

    def makeOrientationFieldsSetupDone(self, make_orientation_fields_settings):
        self.make_orientation_fields_settings = make_orientation_fields_settings
        self.goToNextMenu()

    def startVideoSetup(self):
        self.addForm('MAKE_SNAKE_VIDEOS', MakeSnakeVideosSetupForm, name="Make Snake Videos Setup")
        self.getForm('MAKE_SNAKE_VIDEOS').configure(self.make_snake_videos_settings)
        self.setNextForm('MAKE_SNAKE_VIDEOS')

    def makeSnakeVideosSetupDone(self, make_snake_videos_settings):
        self.make_snake_videos_settings = make_snake_videos_settings
        self.goToNextMenu()
