import sys
import questionary

from altic.logging import info


def prompt_multiple_values(message, choice_func=lambda: True):
    try:
        results = []
        info(message)
        while True:
            choice = questionary.text("Enter value (empty value for finish): ").ask()
            if not choice:
                break
            if choice_func:
                choice_func(choice)
            results.append(choice)
        return results
    except KeyboardInterrupt:
        questionary.print("Exiting...")
        sys.exit(0)


def choose(message, choices):
    return questionary.select(
        message,
        choices=choices
    ).ask()
