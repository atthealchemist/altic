import random
import questionary

from art import text2art


def log(message: str, prefix: str = "",  *args, **kwargs):
    if "new_line" in kwargs:
        kwargs.pop("new_line")
        prefix = f"\n{prefix}"
    questionary.print(f"{prefix} {message}" if prefix else message, *args, **kwargs)


def info(message: str, prefix: str = "ℹ", *args, **kwargs):
    kwargs['style'] = "bold fg:#00BFFF"
    log(message, prefix=prefix, *args, **kwargs)


def warning(message: str, *args, **kwargs):
    kwargs['style'] = "bold fg:yellow"
    log(message, *args, **kwargs)


def error(message: str, prefix: str = "❌", *args, **kwargs):
    kwargs['style'] = "bold fg:red"
    log(message, prefix, *args, **kwargs)


def success(message: str, prefix: str = "✅", *args, **kwargs):
    kwargs['style'] = "bold fg:green"
    log(message, prefix, *args, **kwargs)


def print_logo():
    colors = (
        'cyan',
        'magenta',
        'yellow',
        'green',
        'red',
        'blue',
        'black',
        'orange'
    )
    color = random.choice(colors)
    log(text2art("\naltic", font="univers", chr_ignore=True), style=f"bold fg:{color}")
    log("Packaging without pain and boring legacy manuals\n\n", style=f"bold italic fg:{color}")
