from snakeutils.files import readable_dir
from create_param_files import error_string_or_parse_arg_or_range
from preprocess_tiffs import preprocess_tiffs
from section_tiffs import section_tiffs
from create_param_files import create_param_files
from run_soax_with_params import run_soax_with_params
import npyscreen
import argparse
import os
from snakeutils.logger import RecordLogger

# For parsing setting strings
class ParseException(Exception):
    pass

# For fields that ask for a directory
def check_dir_field(field_name, dir_string, make_dir_if_not_present):
    if dir_string == "":
        return "'{}' is a required field".format(field_name)
    if not os.path.isdir(dir_string):
        if os.path.exists(dir_string):
            return  "'{}' exists but is not a directory".format(dir_string)
        else:
            if make_dir_if_not_present:
                os.makedirs(dir_string)
                return None
            else:
                return "'{}' does not exist".format(dir_string)


class WorkingDirectorySetupForm(npyscreen.Form):
    def configure(self,
        do_preprocess,
        do_section,
        do_create_params,
        do_run_soax,
        do_join_sectioned_snakes,
        do_make_snake_images,
        do_make_videos_from_images,
        ):
        self.do_preprocess = do_preprocess
        self.do_section = do_section
        self.do_create_params = do_create_params
        self.do_run_soax = do_run_soax
        self.do_join_sectioned_snakes = do_join_sectioned_snakes
        self.do_make_snake_images = do_make_snake_images
        self.do_make_videos_from_images = do_make_videos_from_images

        self.check_dir_fields = []
        if self.do_preprocess or self.do_section or self.do_run_soax:
            self.field_raw_src_tiff_dir = self.add(npyscreen.TitleFilename, name="Original TIFF source dir")
            self.check_dir_fields.append(self.field_raw_src_tiff_dir)
        if self.do_preprocess:
            self.field_preprocessed_tiff_dir = self.add(npyscreen.TitleFilename, name="Preprocessed TIFF dir", value="./PreprocessedTIFFs")
            self.check_dir_fields.append(self.field_preprocessed_tiff_dir)
        if self.do_section:
            self.field_sectioned_tiff_dir = self.add(npyscreen.TitleFilename, name="Sectioned TIFF dir", value="./SectionedTIFFs")
            self.check_dir_fields.append(self.field_sectioned_tiff_dir)
        if self.do_create_params or self.do_run_soax:
            self.field_param_files_dir = self.add(npyscreen.TitleFilename, name="Param files dir", value="./Params")
            self.check_dir_fields.append(self.field_param_files_dir)
        if self.do_run_soax or self.do_join_sectioned_snakes or self.do_make_snake_images:
            self.field_snake_files_dir = self.add(npyscreen.TitleFilename, name="Snake files dir", value="./Snakes")
            self.check_dir_fields.append(self.field_snake_files_dir)
        if self.do_run_soax:
            self.field_soax_log_dir = self.add(npyscreen.TitleFilename, name="SOAX logging dir", value="./SoaxLogs")
            self.check_dir_fields.append(self.field_soax_log_dir)
        if self.do_make_snake_images or self.do_make_videos_from_images:
            self.field_snake_images_dir = self.add(npyscreen.TitleFilename, name="Snake images dir", value="./SnakeImages")
            self.check_dir_fields.append(self.field_snake_images_dir)

        self.create_if_not_present = self.add(
            npyscreen.TitleSelectOne,
            name="Create dirs if not present",
            values=["yes", "no"],
            value=[1],
            scroll_exit=True)

    def afterEditing(self):
        # option zero is "yes"
        should_make_dirs = 0 in self.create_if_not_present.value

        # for dir_field in self.check_dir_fields:
        raise Exception("Need to implement checkcing")

        self.parentApp.workingDirSetupDone(
            self.field_raw_src_tiff_dir.value,
            self.field_param_files_dir.value,
            self.field_snake_files_dir.value,
            self.field_soax_log_dir.value,
            self.field_snake_images_dir.value,
            (self.field_preprocessed_tiff_dir.value if self.do_preprocess else None),
            (self.field_sectioned_tiff_dir.value if self.do_section else None),
        )

class StepsSetupForm(npyscreen.Form):
    def configure(self):
        self.select_steps = self.add(
            npyscreen.TitleMultiSelect,
            max_height =-2,
            value = [2,3,5,6],
            name="Pick steps (spacebar to toggle)",
            values = [
                "Preprocess Raw TIFFs",
                "Section TIFFs before running SOAX",
                "Create Parameter Files",
                "Run SOAX",
                "Join Sectioned Snakes together (you should do this if input images to soax are sectioned)",
                "Make images of snakes",
                "Make videos from snake images",
            ],
            scroll_exit=True,
        )

    def afterEditing(self):
        do_preprocess              = 0 in self.select_steps.value
        do_section                 = 1 in self.select_steps.value
        do_create_params           = 2 in self.select_steps.value
        do_run_soax                = 3 in self.select_steps.value
        do_join_sectioned_snakes   = 4 in self.select_steps.value
        do_make_snake_images       = 5 in self.select_steps.value
        do_make_videos_from_images = 6 in self.select_steps.value

        self.parentApp.stagesSelected(
            do_preprocess,
            do_section,
            do_create_params,
            do_run_soax,
            do_join_sectioned_snakes,
            do_make_snake_images,
            do_make_videos_from_images,
        )

class PreprocessSetupForm(npyscreen.Form):
    @staticmethod
    def parseSettings(field_strings, make_dirs_if_not_present=False):
        percentage_fields = ["min_cutoff_percent", "max_cutoff_percent"]
        dir_fields = ["source_image_dir","target_image_dir"]
        parsed_fields = {}

        for field_name in percentage_fields:
            field_str = field_strings[field_name]

            if field_str == "":
                raise ParseException("'{}' is a required field".format(field_name))
            try:
                perc = float(field_str)
            except ValueError:
                raise ParseException("'{}' value '{}' is not a number".format(field_name,field_str))

            perc = float(field_str)

            if perc < 0 or perc > 100:
                raise ParseException("Invalid '{}' value '{}': should be between 0 and 100".format(field_name,str(perc)))

            parsed_fields[field_name] = perc

        for field_name in dir_fields:
            field_str = field_strings[field_name]
            err = check_dir_field(field_name, field_str, make_dirs_if_not_present)
            if err is not None:
                raise ParseException(err)

            parsed_fields[field_name] = field_str

        return parsed_fields

    def configure(self, preprocess_settings):
        self.field_source_dir = self.add(npyscreen.TitleFilename, name="source_image_dir",
            value=preprocess_settings["source_image_dir"])
        self.field_target_dir = self.add(npyscreen.TitleFilename, name="target_image_dir",
            value=preprocess_settings["target_image_dir"])

        self.field_min_cutoff_percent = self.add(
            npyscreen.TitleFilename,
            value=preprocess_settings["min_cutoff_percent"],
            name="min_cutoff_percent")
        self.field_max_cutoff_percent = self.add(
            npyscreen.TitleFilename,
            value=preprocess_settings["max_cutoff_percent"],
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
            "max_cutoff_percent": self.field_min_cutoff_percent.value,
            "min_cutoff_percent": self.field_min_cutoff_percent.value,
            "source_image_dir": self.field_source_dir.value,
            "target_image_dir": self.field_target_dir.value,
        }

    def afterEditing(self):
        # option zero is "yes"
        make_dirs_if_not_present = 0 in self.create_if_not_present.value

        try:
            self.parseSettings(self.getFieldStrings(), make_dirs_if_not_present)
        except ParseException as e:
            npyscreen.notify_confirm(str(e),editw=1)
            return

        self.parentApp.preprocessSetupDone(self.getFieldStrings())

class SectioningSetupForm(npyscreen.Form):
    @staticmethod
    def parseSettings(field_strings, make_dirs_if_not_present):
        pos_int_fields = ["section_max_size"]
        dir_fields = ["source_image_dir","target_sectioned_image_dir"]
        parsed_fields = {}

        for field_name in pos_int_fields:
            field_str = field_strings[field_name]
            if field.value == ""
                raise ParseException("'{}' is a required field".format(field_name))
            try:
                field_val = int(field_str)
            except ValueError as e:
                raise ParseException("Cannot parse '{}' value '{}' as integer".format(field_name,field_str))
            if field_val <= 0:
                raise ParseException("Field '{}' has invalid value '{}': must be positive integer".format(field_name, field_str))

        for field_name in dir_fields:
            field_str = field_strings[field_name]
            err = check_dir_field(field_name, field_str, make_dirs_if_not_present)
            if err is not None:
                raise ParseException(err)

            parsed_fields[field_name] = field_str

        return parsed_fields

    def configure(self, sectioning_settings):
        self.field_source_dir = self.add(npyscreen.TitleFilename, name="source_image_dir",
            value=preprocess_settings["source_image_dir"])
        self.field_sectioned_target_dir = self.add(npyscreen.TitleFilename, name="target_sectioned_image_dir",
            value=preprocess_settings["target_sectioned_image_dir"])

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
            "source_image_dir": self.field_source_dir.value,
            "target_sectioned_image_dir": self.field_sectioned_target_dir,
            "section_max_size": self.field_section_max_size.value,
        }

    def afterEditing(self):
        # option zero is "yes"
        make_dirs_if_not_present = 0 in self.create_if_not_present.value

        try:
            self.parseSettings(self.getFieldStrings(), make_dirs_if_not_present)
        except ParseException as e:
            npyscreen.notify_confirm(str(e),editw=1)
            return

        self.parentApp.sectioningSetupDone(
            int(self.section_max_size.value),
        )

class ParamsSetupForm(npyscreen.Form):
    @staticmethod
    def parseSettings(field_strings, make_dirs_if_not_present=False):
        parsed_fields = {}
        arg_or_range_fields = ["alpha", "beta", "min_foreground", "ridge_threshold"]
        dir_fields = ["source_image_dir", "target_image_dir"]

        for field_name in arg_or_range_fields:
            field_str = field_strings[field_name]

            if field_str == "":
                raise ParseException("'{}' is a required field")

            err_str_or_val = error_string_or_parse_arg_or_range(field_str)
            if isinstance(err_str_or_val, str):
                raise ParseException("Error parsing {}: {}".format(field_name, err_str_or_val))
            else:
                parsed_fields[field_name] = err_str_or_val

        for field_name in dir_fields:
            field_str = field_strings[field_name]
            err = check_dir_field(field_name, field_str, make_dirs_if_not_present)
            if err is not None:
                raise ParseException(err)

            parsed_fields[field_name] = field_str

        return parsed_fields

    def configure(self, params_settings):
        self.add(npyscreen.FixedText,
            value="Enter SOAX run parameters to try.")
        self.add(npyscreen.FixedText,
            value="Enter number values (ex. 1,3.44,10.3) or start-stop-step ranges (ex. 1-20-0.5,1.5-3.5-1.0)")
        self.add(npyscreen.FixedText,
            value="If ranges are given, soax will be run multiple times, trying all combinations of parameter values")

        self.field_source_dir = self.add(npyscreen.TitleFilename, name="Source TIFF dir",
            value=preprocess_settings["source_image_dir"])
        self.field_target_dir = self.add(npyscreen.TitleFilename, name="Target TIFF dir",
            value=preprocess_settings["target_image_dir"])

        self.field_alpha           = self.add(npyscreen.TitleText, name="alpha",
            value=params_settings["alpha"])
        self.field_beta            = self.add(npyscreen.TitleText, name="beta",
            value=params_settings["beta"])
        self.field_min_foreground  = self.add(npyscreen.TitleText, name="min_foreground",
            value=params_settings["min_foreground"])
        self.field_ridge_threshold = self.add(npyscreen.TitleText, name="ridge_threshold",
            value=params_settings["ridge_threshold"])

        self.create_if_not_present = self.add(
            npyscreen.TitleSelectOne,
            name="Create dirs if not present",
            values=["yes", "no"],
            value=[1],
            scroll_exit=True)

    def getFieldStrings(self):
        return {
            "alpha": self.field_alpha.value,
            "beta": self.field_beta.value,
            "min_foreground": self.field_min_foreground.value,
            "ridge_threshold": self.field_ridge_threshold.value,
        }

    def afterEditing(self):
        # option zero is "yes"
        make_dirs_if_not_present = 0 in self.create_if_not_present.value

        try:
            self.parseSettings(self.getFieldStrings(), make_dirs_if_not_present)
        except ParseException as e:
            npyscreen.notify_confirm(str(e),editw=1)
            return

        self.parentApp.paramsSetupDone(self.getFieldStrings())

class SoaxRunSetupForm(npyscreen.Form):
    def configure(self, source_sectioned):
        self.field_soax_executable_path = self.add(npyscreen.TitleFilename, name="batch soax executable", value="/home/paul/Documents/build_soax_july3_follow_ubuntu_18_guide/build_soax/batch_soax")
        self.field_worker_number = self.add(npyscreen.TitleFilename, name="Workers count (number of batch_soax instances to run at once)", value="5")

        self.use_subdirs = self.add(
            npyscreen.TitleSelectOne,
            name="Expect source images to be in subdirectories (should be true if images are sectioned)",
            values=["yes", "no"],
            value=([0] if source_sectioned else [1]),
            scroll_exit=True)

    def afterEditing(self):
        use_subdirs = 0 in self.use_subdirs.value

        if self.field_soax_executable_path.value == "":
            npyscreen.notify_confirm(
                "'{}' is a required field".format(self.field_soax_executable_path.name),
                editw=1,
            )
            return
        if not os.path.exists(self.field_soax_executable_path.value):
            npyscreen.notify_confirm("'{}' does not exist".format(self.field_soax_executable_path.value),editw=1)
            return
        if os.path.isdir(self.field_soax_executable_path.value):
            npyscreen.notify_confirm(
                "'{}' is a directory, should be executable file".format(self.field_soax_executable_path.value),
                editw=1,
            )
            return

        if self.field_worker_number.value == "":
            npyscreen.notify_confirm(
                "{} is a required field".format(self.field_worker_number.name),
                editw=1,
            )
            return
        try:
            int(self.field_worker_number.value)
        except ValueError as e:
            npyscreen.notify_confirm(
                "Cannot parse '{}' value '{}' as integer".format(self.field_worker_number.name, self.field_worker_number.value),
                editw=1,
            )
            return
        if int(self.field_worker_number.value) <= 0:
            npyscreen.notify_confirm(
                "Value of '{}' must be greater or equal to one".format(self.field_worker_number.name),
                editw=1,
            )
            return

        self.parentApp.soaxRunSetupDone(
            self.field_soax_executable_path.value,
            int(self.field_worker_number.value),
            use_subdirs,
        )

class SoaxHelperApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.preprocess_settings = {
            "max_cutoff_percent": "95.5",
            "min_cutoff_percent": "0.1",
            "source_image_dir": "",
            "target_image_dir": "",
        }
        self.sectioning_settings = {
            "source_image_dir": "",
            "target_sectioned_image_dir": "",
            "section_max_size": "200",
        }
        self.params_settings = {
            "alpha": "0.01",
            "beta": "0.1",
            "min_foreground": "10"
            "ridge_threshold": "0.01",
        }
        self.soax_run_settings = None
        self.joinSectionedSnakesSettings = None
        self.snakeImagesSettings = None
        self.videoSettings = None

        self.addForm('MAIN', StepsSetupForm, name='Select Steps')
        self.getForm('MAIN').configure()

    def stagesSelected(self,
        do_preprocess,
        do_section,
        do_create_params,
        do_run_soax,
        do_join_sectioned_snakes,
        do_make_snake_images,
        do_make_videos_from_images,
        ):
        self.do_preprocess = do_preprocess
        self.do_section = do_section
        self.do_create_params = do_create_params
        self.do_run_soax = do_run_soax
        self.do_join_sectioned_snakes = do_join_sectioned_snakes
        self.do_make_snake_images = do_make_snake_images
        self.do_make_videos_from_images = do_make_videos_from_images

        self.menu_functions = []
        if self.do_preprocess:
            self.menu_functions.append(self.startPreprocessSetup)
        if self.do_section:
            self.menu_functions.append(self.startSectioningSetup)
        if self.do_create_params:
            self.menu_functions.append(self.startParamSetup)
        if self.do_run_soax:
            self.menu_functions.append(self.startSoaxRunSetup)
        if self.do_join_sectioned_snakes:
            self.menu_functions.append(self.startJoinSectionedSnakesSetup)
        if self.do_make_snake_images:
            self.menu_functions.append(self.startSnakeImagesSetup)
        if self.do_make_videos_from_images:
            self.menu_functions.append(self.startVideoSetup)

        self.goToNextMenu()

    def goToNextMenu(self):
        if len(self.menu_functions) == 0:
            self.setNextForm(None)
        else:
            next_menu_func = self.menu_functions.pop(0)
            next_menu_func()

    def startPreprocessSetup(self):
        self.addForm('PREPROCESS_SETUP', PreprocessSetupForm, name='Preprocessing Setup')
        self.getForm('PREPROCESS_SETUP').configure(self.preprocess_settings)
        self.setNextForm('PREPROCESS_SETUP')

    def preprocessSetupDone(self, preprocess_settings):
        self.preprocess_settings = preprocess_settings
        self.sectioning_settings["source_image_dir"] = preprocess_settings["target_image_dir"]
        self.goToNextMenu()

    def startSectioningSetup(self):
        self.addForm('SECTIONING_SETUP', SectioningSetupForm, name='Sectioning Setup')
        self.getForm('SECTIONING_SETUP').configure(self.sectioning_settings)
        self.setNextForm('SECTIONING_SETUP')

    def sectioningSetupDone(self, sectioning_settings):
        self.sectioning_settings = sectioning_settings
        self.goToNextMenu()

    def startParamSetup(self):
        self.addForm('PARAM_SETUP', ParamsSetupForm, name="SOAX Params Setup")
        self.getForm('PARAM_SETUP').configure(self.params_settings)
        self.setNextForm('PARAM_SETUP')

    def paramsSetupDone(self, params_settings):
        self.params_settings = params_settings
        self.goToNextMenu()

    def startSoaxRunSetup(self):
        self.addForm('SOAX_RUN_SETUP', SoaxRunSetupForm, name="SOAX Run Setup")
        self.getForm('SOAX_RUN_SETUP').configure(self.do_section)
        self.setNextForm('SOAX_RUN_SETUP')

    def soaxRunSetupDone(self, batch_soax_path, workers_num):
        self.soax_run_settings = {
            "batch_soax_path": batch_soax_path,
            "workers_num": workers_num,
        }
        self.goToNextMenu()

    def startJoinSectionedSnakesSetup(self):
        raise NotImplementedError("Unimplemented")

    def joinSectionedSnakesSetupDone(self):
        self.joinSectionedSnakesSettings = {}

    def startSnakeImagesSetup(self):
        raise NotImplementedError("Unimplemented")

    def makeSnakeImagesSetupDone(self):
        self.snakeImagesSettings = {}

    def startVideoSetup(self):
        raise NotImplementedError("Unimplemented")

    def videoSetupDone(self):
        self.videoSettings = {}

if __name__ == "__main__":
    app = SoaxHelperApp()
    app.run()

    if app.do_preprocess:
        preprocess_logger = RecordLogger()

        parsed_preprocess_settings = PreprocessSetupForm.parseSettings(app.preprocess_settings)

        preprocess_tiffs(
            parsed_preprocess_settings["source_image_dir"],
            parsed_preprocess_settings["target_image_dir"],
            parsed_preprocess_settings["max_cutoff_percent"],
            parsed_preprocess_settings["min_cutoff_percent"],
            logger=preprocess_logger,
        )

    if app.do_section:
        sectioning_logger = RecordLogger()

        parsed_sectioning_settings = SectioningSetupForm.parseSettings(app.sectioning_settings)

        section_tiffs(
            parsed_sectioning_settings["section_max_size"],
            parsed_sectioning_settings["source_image_dir"],
            parsed_sectioning_settings["target_sectioned_image_dir"],
            logger=sectioning_logger,
        )

    if app.do_create_params:
        create_params_logger = RecordLogger()
        create_param_files(
            app.workingDirSettings["param_files_dir"],
            app.params_settings["alpha"],
            app.params_settings["beta"],
            app.params_settings["min_foreground"],
            app.params_settings["ridge_threshold"],
            logger=PrintLogger
        )

    if app.do_run_soax:
        if app.do_section:
            soax_source_dir = app.workingSettings["sectioned_tiff_dir"]
        elif app.do_preprocess:
            soax_source_dir = app.workingSettings["preprocessed_tiff_dir"]
        else:
            soax_source_dir = app.workingDirSettings["raw_src_tiff_dir"]

        # if each image is split into section tiffs inside a new subdirectory, we use subdirs
        soax_use_subdirs = app.do_section

        soax_logger = RecordLogger()
        run_soax_with_params(
            app.soax_run_settings["batch_soax_path"],
            soax_source_dir,
            app.workingDirSettings["param_files_dir"],
            app.workingDirSettings["snake_files_dir"],
            app.workingDirSettings["soax_log_dir"],
            soax_use_subdirs,
            app.soax_run_settings["workers_num"],
            logger=soax_logger)

