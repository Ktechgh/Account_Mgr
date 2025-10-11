 
import sys
import os


# Custom ANSI escape codes
CUSTOM_COLORS = {
    "GREEN": "\033[92m",
    "RED": "\033[91m",
    "YELLOW": "\033[93m",
    "RESET": "\033[0m",
}

# No color fallback
NO_COLOR = {
    "GREEN": "",
    "RED": "",
    "YELLOW": "",
    "RESET": "",
}

def get_color_support():
    # Dynamically returns the best color support depending on the environment.
    # - VS Code => colorama
    # - Sublime Text or others => ANSI (custom)
    # - Fallback => no color
    try:
        # If output is a real terminal
        if sys.stdout.isatty():
            # VS Code specific: has full ANSI + colorama support
            if "VSCODE_PID" in os.environ:
                from colorama import init, Fore, Style

                init(autoreset=True)
                return {
                    "GREEN": Fore.GREEN,
                    "RED": Fore.RED,
                    "YELLOW": Fore.YELLOW,
                    "RESET": Style.RESET_ALL,
                }

            # Other terminals that support ANSI (like CMD, Linux)
            return CUSTOM_COLORS

    except Exception:
        pass

    # Fallback (Sublime Text or broken shell)
    return NO_COLOR
