import re


def snake_to_capital(value: str) -> str:
    """
    Converts snake_case string to CapitalCase.
    
    Example:
    >>> snake_to_capital("build_requires")
    "BuildRequires"
    >>> snake_to_capital("requires")
    "Requires"

    Args:
        value (str): snake_case style string

    Returns:
        str: CapitalCase style string
    """
    if "_" in value:
        return "".join([s.title() for s in value.split("_")])
    return value.capitalize()


def capital_to_snake(value):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', value).lower()


def plural(value: str) -> str:
    return value.rstrip("aouie") + "es"
