# Raymond Liu 101264487
# Afaq Virk 101338854
# CLI helpers + pretty print


import os
import time
from typing import List

try:
    from colorama import init as colorama_init, Fore, Style
except ImportError:
    Fore = type("Fore", (), {"RED": "", "GREEN": "", "YELLOW": "", "CYAN": "", "MAGENTA": "", "WHITE": ""})
    Style = type("Style", (), {"BRIGHT": "", "RESET_ALL": ""})


def init_console() -> None:
    """Initialize console color support (Windows-safe)."""
    try:
        colorama_init(autoreset=True)
    except Exception:
        pass


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def color_text(text: str, color: str = "", bold: bool = False) -> str:
    """Return text wrapped with style codes."""
    prefix = ""
    if bold:
        prefix += Style.BRIGHT
    if color:
        prefix += color
    return f"{prefix}{text}{Style.RESET_ALL}"


def header(title: str) -> None:
    """Render a styled section header."""
    bar = "=" * (len(title) + 4)
    print(color_text(bar, Fore.MAGENTA, True))
    print(color_text(f"  {title}  ", Fore.MAGENTA, True))
    print(color_text(bar, Fore.MAGENTA, True))


def menu(title: str, options: List[str]) -> str:
    """Render a styled menu and return the user's raw choice."""
    clear_screen()
    header(title)
    for idx, opt in enumerate(options, 1):
        print(color_text(f"{idx}. {opt}", Fore.CYAN))
    print()
    return input(color_text("Choice: ", Fore.WHITE, True)).strip()


def pause() -> None:
    """Wait for user to press Enter."""
    input(color_text("\nPress Enter to continue...", Fore.WHITE))


def success(msg: str) -> None:
    print(color_text(msg, Fore.GREEN, True))


def error(msg: str) -> None:
    print(color_text(msg, Fore.RED, True))


def warn(msg: str) -> None:
    print(color_text(msg, Fore.YELLOW, True))


def info(msg: str) -> None:
    print(color_text(msg, Fore.CYAN))


def sleep(seconds: float) -> None:
    try:
        time.sleep(seconds)
    except Exception:
        pass

