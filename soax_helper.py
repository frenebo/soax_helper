from snakeutils.files import readable_dir
from create_param_files import error_string_or_parse_arg_or_range
from preprocess_tiffs import preprocess_tiffs
import npyscreen
import argparse
import os

class WorkingDirectorySetupForm(npyscreen.Form):
    def create(self):
        self.field_raw_src_tiff_dir = self.add(npyscreen.TitleFilename, name="Raw TIFF source dir")
        self.field_preprocessed_tiff_dir = self.add(npyscreen.TitleFilename, name="Preprocessed TIFF dir")
        self.field_param_files_dir = self.add(npyscreen.TitleFilename, name="Param files save dir")
        self.field_snake_files_dir = self.add(npyscreen.TitleFilename, name="Snake files dir")
        self.field_soax_log_dir = self.add(npyscreen.TitleFilename, name="SOAX logging dir")
        self.field_snake_images_dir = self.add(npyscreen.TitleFilename, name="Snake images dir")

    def afterEditing(self):
        check_dir_fields = [
            self.field_raw_src_tiff_dir,
            self.field_preprocessed_tiff_dir,
            self.field_param_files_dir,
            self.field_snake_files_dir,
            self.field_soax_log_dir,
            self.field_snake_images_dir,
        ]
        for dir_field in check_dir_fields:
            if dir_field.value == "":
                npyscreen.notify_confirm("'{}' is a required field".format(dir_field.name),editw=1)
                return
            if not os.path.isdir(dir_field.value):
                if os.path.exists(dir_field.value):
                    npyscreen.notify_confirm("'{}' exists but is not a directory".format(dir_field.value),editw=1)
                    return
                else:
                    npyscreen.notify_confirm("'{}' does not exist".format(dir_field.value),editw=1)
                    return

        self.parentApp.workingDirSetupDone(
            self.field_raw_src_tiff_dir.value,
            self.field_preprocessed_tiff_dir.value,
            self.field_param_files_dir.value,
            self.field_snake_files_dir.value,
            self.field_soax_log_dir.value,
            self.field_snake_images_dir.value,
        )

class PreprocessSetupForm(npyscreen.Form):
    def create(self):
        pass

    def afterEditing(self):
        self.parentApp.preprocessSetupDone()
        pass

class ParamsForm(npyscreen.Form):
    def create(self):
        self.instructions = self.add(npyscreen.FixedText,
            value="Either enter number values (ex. 1,3.44,10.3) or start-stop-step ranges (ex. 1-20-0.5,1.5-3.5-1.0)")
        self.field_alpha           = self.add(npyscreen.TitleText, name="alpha", value="0.01")
        self.field_beta            = self.add(npyscreen.TitleText, name="beta", value="0.1")
        self.field_min_foreground  = self.add(npyscreen.TitleText, name="min_foreground", value="10")
        self.field_ridge_threshold = self.add(npyscreen.TitleText, name="ridge_threshold", value="0.01")

    def afterEditing(self):
        check_arg_or_range_fields = [
            self.field_alpha,
            self.field_beta,
            self.field_min_foreground,
            self.field_ridge_threshold,
        ]
        for field in check_arg_or_range_fields:
            if field.value == "":
                npyscreen.notify_confirm("'{}' is a required field".format(field.name),editw=1)
                return

            err_str_or_val = error_string_or_parse_arg_or_range(field.value)
            if isinstance(err_str_or_val, str):
                npyscreen.notify_confirm("Error parsing {}: {}".format(field.name, err_str_or_val),editw=1)
                return


        self.parentApp.paramsSetupDone(
            error_string_or_parse_arg_or_range(self.field_alpha.value),
            error_string_or_parse_arg_or_range(self.field_beta.value),
            error_string_or_parse_arg_or_range(self.field_min_foreground.value),
            error_string_or_parse_arg_or_range(self.field_ridge_threshold.value),
        )

class PreprocessForm(npyscreen.Form):
    def create(self):
        preprocess_settings = self.parentApp.getPreprocessSettings()

        preprocess_tiffs(
            preprocess_settings["source_dir"],
            preprocess_settings["target_dir"],
            preprocess_settings["max_cutoff_percent"],
            preprocess_settings["min_cutoff_percent"],
        )

        self.parentApp.preprocessDone()
        pass

class SoaxHelperApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', WorkingDirectorySetupForm, name='Select Working Directories')


    def workingDirSetupDone(self,
        raw_src_tiff_dir,
        preprocessed_tiff_dir,
        param_files_dir,
        snake_files_dir,
        soax_log_dir,
        snake_images_dir,
        ):
        self.workingDirSettings = {
            "raw_src_tiff_dir": raw_src_tiff_dir,
            "preprocessed_tiff_dir": preprocessed_tiff_dir,
            "param_files_dir": param_files_dir,
            "snake_files_dir": snake_files_dir,
            "soax_log_dir": soax_log_dir,
            "snake_images_dir": snake_images_dir,
        }
        self.addForm('PREPROCESS_SETUP', PreprocessSetupForm, name='Preprocessing Setup')
        self.setNextForm('PREPROCESS_SETUP')

    def preprocessSetupDone(self,
        max_cutoff_percent,
        min_cutoff_percent,
        ):
        self.preprocessSettings = {
            "source_dir": self.workingDirSettings["raw_src_tiff_dir"],
            "target_dir": self.workingDirSettings["preprocessed_tiff_dir"],
            "max_cutoff_percent": max_cutoff_percent,
            "min_cutoff_percent": min_cutoff_percent,
        }
        self.addForm('PARAM_SETUP', ParamsForm, name="Params Setup")
        self.setNextForm('PARAM_SETUP')

    def paramsSetupDone(self,
        alpha,
        beta,
        min_foreground,
        ridge_threshold,
        ):
        self.alpha = alpha
        self.beta = beta
        self.min_foreground = min_foreground
        self.ridge_threshold = ridge_threshold

        self.addForm('PREPROCESS', PreprocessForm, name="Preprocessing Images")
        self.setNextForm('PREPROCESS')

    def getPreprocessSettings(self):
        return self.preprocessSettings

    def preprocessDone(self):
        self.setNextForm(None)

if __name__ == "__main__":
    app = SoaxHelperApp()
    app.run()