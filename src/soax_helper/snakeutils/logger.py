from colorama import Fore, Style

class FileLogger:
    def __init__(self, log_filehandle, parent_logger):
        self.log_filehandle = log_filehandle
        self.parent_logger = parent_logger

    def log(self, text):
        self.log_filehandle.write('LOG: ' + text + '\n')
        self.parent_logger.log(text)

    def warn(self, text):
        self.log_filehandle.write('WARN: ' + text + '\n')
        self.parent_logger.warn(text)

    def success(self, text):
        self.log_filehandle.write('SUCCESS: ' + text + '\n')
        self.parent_logger.success(text)

    def error(self, text):
        self.log_filehandle.write('ERROR: ' + text + '\n')
        self.parent_logger.error(text)

    def FAIL(self, text):
        self.log_filehandle.write('FAIL: ' + text + '\n')
        self.parent_logger.FAIL(text)

class RecordingLogger:
    def __init__(self, parent_logger):
        self.parent_logger = parent_logger

        self.normal_logs = []
        self.successes = []
        self.errors = []
        self.warnings = []
        self.fails = []

    def log(self,text):
        self.normal_logs.append(text)
        self.parent_logger.log(text)

    def warn(self, text):
        self.warnings.append(text)
        self.parent_logger.warn(text)

    def success(self,text):
        self.successes.append(text)
        self.parent_logger.success(text)

    def error(self,text):
        self.errors.append(text)
        self.parent_loggerr.error(text)

    def FAIL(self,text):
        self.fails.append(text)
        self.parent_logger.FAIL(text)

class LoggerFAILCalledException(Exception):
    pass

class ConsoleLogger:
    def log(self, text):
        print(text)

    def warn(self, text):
        print(Fore.YELLOW + text + Style.RESET_ALL)

    def success(self, text):
        print(Fore.GREEN + text + Style.RESET_ALL)

    def error(self, text):
        print(Fore.RED + text + Style.RESET_ALL)

    def FAIL(self, text):
        raise LoggerFAILCalledException(text)
