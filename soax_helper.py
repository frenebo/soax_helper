from snakeutils.files import readable_dir
from create_param_files import error_string_or_parse_arg_or_range
import npyscreen
import argparse
import os

class SoaxSetupForm(npyscreen.Form):
    def create(self):
        self.field_raw_src_tiff_dir = self.add(npyscreen.TitleFilename, name="Raw TIFF source dir")
        self.field_param_files_dir  = self.add(npyscreen.TitleFilename, name="Param files save dir")
        self.field_snake_files_dir  = self.add(npyscreen.TitleFilename, name="Snake files dir")
        self.field_soax_log_dir     = self.add(npyscreen.TitleFilename, name="SOAX logging dir")
        self.field_snake_images_dir = self.add(npyscreen.TitleFilename, name="Snake images dir")
        # self.myName        = self.add(npyscreen.TitleText, name='Name')
        # self.myDepartment = self.add(npyscreen.TitleSelectOne, scroll_exit=True, max_height=3, name='Department', values = ['Department 1', 'Department 2', 'Department 3'])
        # self.myDate        = self.add(npyscreen.TitleDateCombo, name='Date Employed')

    def afterEditing(self):
        check_dir_fields = [
            self.field_raw_src_tiff_dir,
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

        self.parentApp.soaxSetupDone(
            self.field_raw_src_tiff_dir.value,
            self.field_param_files_dir.value,
            self.field_snake_files_dir.value,
            self.field_soax_log_dir.value,
            self.field_snake_images_dir.value,
        )

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


        self.parentApp.paramsSetupDone()

class SoaxHelperApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', SoaxSetupForm, name='Setup Form')
        self.addForm('PARAMS', ParamsForm, name="Params Setup")

    def soaxSetupDone(self,
        raw_src_tiff_dir,
        param_files_dir,
        snake_files_dir,
        soax_log_dir,
        snake_images_dir,
        ):
        self.raw_src_tiff_dir = raw_src_tiff_dir
        self.param_files_dir = param_files_dir
        self.snake_files_dir = snake_files_dir
        self.soax_log_dir = soax_log_dir
        self.snake_images_dir = snake_images_dir
        self.setNextForm('PARAMS')

    def paramsSetupDone(self):
        self.setNextForm(None)


if __name__ == "__main__":
    app = SoaxHelperApp()
    app.run()