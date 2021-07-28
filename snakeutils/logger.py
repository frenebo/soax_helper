from colorama import Fore, Style
import threading

class Colors:
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"

class PagerFailError(Exception):
    pass

class PagerLogger:
    def __init__(self, pager):
        self.pager = pager
        self.lock = threading.Lock()

        self.error_lines = []
        self.fail_lines = []

    def log(self,text):
        with self.lock:
            self.pager.values.append(text)
            self.pager.update()

    def error(self,text):
        with self.lock:
            self.error_lines.append(text)
            self.pager.values.append(text)
            self.pager.update()

    def FAIL(self,text):
        with self.lock:
            self.pager.values.append(text)
            self.pager.update()

            raise PagerFailError(text)

class PrintLogger:
    @staticmethod
    def log(text):
        print(text)

    @staticmethod
    def success(text):
        print(Fore.GREEN + text + Style.RESET_ALL)

    @staticmethod
    def error(text):
        print(Fore.RED + text + Style.RESET_ALL)

    @staticmethod
    def FAIL(text):
        raise Exception(text)
