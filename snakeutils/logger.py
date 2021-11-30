from colorama import Fore, Style


class RecordLogger:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.fails = []

    def log(self,text):
        PrintLogger.log(text)

    def warn(self, text):
        self.warnings.append(text)
        PrintLogger.warn(text)

    def success(self,text):
        PrintLogger.success(text)

    def error(self,text):
        self.errors.append(text)
        PrintLogger.error(text)

    def FAIL(self,text):
        self.fails.append(text)
        PrintLogger.FAIL(text)

class LoggerFAILCalledException(Exception):
    pass

class PrintLogger:
    @staticmethod
    def log(text):
        print(text)

    @staticmethod
    def warn(text):
        print(Fore.YELLOW + text + Style.RESET_ALL)

    @staticmethod
    def success(text):
        print(Fore.GREEN + text + Style.RESET_ALL)

    @staticmethod
    def error(text):
        print(Fore.RED + text + Style.RESET_ALL)

    @staticmethod
    def FAIL(text):
        raise LoggerFAILCalledException(text)
