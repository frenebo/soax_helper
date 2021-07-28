from colorama import Fore, Style

class Colors:
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"

def get_colorama_fore_color(color):
    if color == Colors.RED:
        return Fore.RED
    elif color == Colors.YELLOW:
        return Fore.YELLOW
    elif color == Colors.GREEN:
        return Fore.Green:
    else:
        raise ValueError("Unsupported colorama color {}".format(color))

class PrintLogger:
    @staticmethod
    def log(text, color=None):
        if color is not None:
            print(get_colorama_fore_color(color) + text + Style.RESET_ALL)
        else:
            print(text)