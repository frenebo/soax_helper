from snakeutils.files import readable_dir
from create_param_files import error_string_or_parse_arg_or_range
from preprocess_tiffs import preprocess_tiffs
import npyscreen
import argparse
import os
from snakeutils.logger import PagerLogger, PagerFailError
import threading

class WorkingDirectorySetupForm(npyscreen.Form):
    def create(self):
        self.field_raw_src_tiff_dir = self.add(npyscreen.TitleFilename, name="Raw TIFF source dir")
        self.field_preprocessed_tiff_dir = self.add(npyscreen.TitleFilename, name="Preprocessed TIFF dir", value="./PreprocessedTIFFs")
        self.field_param_files_dir = self.add(npyscreen.TitleFilename, name="Param files save dir", value="./Params")
        self.field_snake_files_dir = self.add(npyscreen.TitleFilename, name="Snake files dir", value="./Snakes")
        self.field_soax_log_dir = self.add(npyscreen.TitleFilename, name="SOAX logging dir", value="./SoaxLogs")
        self.field_snake_images_dir = self.add(npyscreen.TitleFilename, name="Snake images dir", value="./SnakeImages")
        self.create_if_not_present = self.add(npyscreen.TitleSelectOne, name="Create dirs if not present", values=["yes", "no"],value=[1],scroll_exit=True)


    def afterEditing(self):
        # option zero is "yes"
        should_make_dirs = self.create_if_not_present.value[0] == 0

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
                    if should_make_dirs:
                        os.makedirs(dir_field.value)
                    else:
                        # if self.
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
        self.field_min_cutoff_percent = self.add(npyscreen.TitleFilename, value="95.5", name="min cutoff percent")
        self.field_max_cutoff_percent = self.add(npyscreen.TitleFilename, value="0.1", name="max cutoff percent")

        npyscreen.notify_confirm(
            "Min and max cutoff percent are brightness level percentiles to use to rescale the TIFF image brightnesses " +
            "min=1 and max=99 would find the brightness that only 1% of tiff pixels in the first TIF in the directory are dimmer than, " +
            "and the brightness that 99% of tiff pixels are dimmer than. The 1% brightness is the lower threshold, and 99% brightness is the upper threhold. " +
            "All pixels dimmer than the lower threshold are set to total black, all pixels brighter than the upper threshold are set to pure white, " +
            "and pixel brightnesses in between are rescaled to a new value between total black and total white",
            wide=True,
            editw=1,
        )


    def afterEditing(self):
        check_percentage_fields = [
            self.field_min_cutoff_percent,
            self.field_max_cutoff_percent,
        ]
        for field in check_percentage_fields:
            if field.value == "":
                npyscreen.notify_confirm("'{}' is a required field".format(field.name),editw=1)
                return
            try:
                float(field.value)
            except ValueError:
                npyscreen.notify_confirm("'{}' value '{}' is not a number".format(field.name,field.value),editw=1)
                return
            perc = float(field.value)
            if perc < 0 or perc > 100:
                npyscreen.notify_confirm("Invalid '{}' value '{}': should be between 0 and 100".format(field.name,str(perc)),editw=1)
                return

        self.parentApp.preprocessSetupDone(
            float(self.field_min_cutoff_percent.value),
            float(self.field_max_cutoff_percent.value),
        )

class ParamsForm(npyscreen.Form):
    def create(self):
        self.add(npyscreen.FixedText,
            value="Enter SOAX run parameters to try.")
        self.add(npyscreen.FixedText,
            value="Enter number values (ex. 1,3.44,10.3) or start-stop-step ranges (ex. 1-20-0.5,1.5-3.5-1.0)")
        self.add(npyscreen.FixedText,
            value="If ranges are given, soax will be run multiple times, trying all combinations of parameter values")
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

def do_preprocess(logger, on_finish):
    try:
        preprocess_tiffs(
            preprocess_settings["source_dir"],
            preprocess_settings["target_dir"],
            preprocess_settings["max_cutoff_percent"],
            preprocess_settings["min_cutoff_percent"],
            logger=logger,
        )
    except PagerFailError as e:
        err_string = repr(e)
        npyscreen.notify_confirm("Fatal Failure: " + err_string,editw=1,wide=True)
        exit()

    if len(logger.error_lines) > 0:
        npyscreen.notify_confirm("Encountered errors: " + ",".join(logger.error_lines), editw=1,wide=True)

    on_finish()

class PreprocessForm(npyscreen.Form):
    def create(self):
        preprocess_settings = self.parentApp.getPreprocessSettings()

        pager = self.add(npyscreen.Pager, name="Preprocess Progress")
        self.logger = PagerLogger(pager)
        self.done = False

        preprocess_thread = threading.Thread(target=do_preprocess,args=(self.logger,self.finish,))


    def afterEditing(self):
        if not self.done:
            npyscreen.notify_confirm("Not done preprocessing images",editw=1)
            return
        else:
            self.parentApp.preprocessDone()

    def finish(self):
        self.done = True

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

        self.beginRunningSteps()

    def beginRunningSteps(self):
        execute_steps = [
            ["PREPROCESS", PreprocessForm, "Preprocess Images"],
        ]

        do_execute = npyscreen.notify_ok_cancel(
            "Execute following steps?: {}".format(",".join([step[2] for step in execute_steps])),
            editw=1
        )

        if not do_execute:
            exit()

        for step_code,step_form,step_name in execute_steps:
            self.addForm(step_code,step_form,name=step_name)
            self.setNextForm(step_code)
        # self.addForm('PREPROCESS', PreprocessForm, name="Preprocessing Images")
        # self.setNextForm('PREPROCESS')

    def getPreprocessSettings(self):
        return self.preprocessSettings

    def preprocessDone(self):
        # npyscr
        self.setNextForm(None)
        # exit()

if __name__ == "__main__":
    app = SoaxHelperApp()
    app.run()