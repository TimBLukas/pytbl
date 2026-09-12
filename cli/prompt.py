"""User prompt helpers for interactive command-line tools."""

from __future__ import annotations

from getpass import getpass
from typing import Callable, Sequence


def prompt(
    message: str,
    *,
    default: str | None = None,
    validator: Callable[[str], bool] | None = None,
    secret: bool = False,
    empty_ok: bool = False,
) -> str:
    """Prompt the user for a string value until validation succeeds."""

    while True:
        if secret:
            value = getpass(f"{message}: ")
        else:
            suffix = f" [{default}]" if default is not None else ""
            value = input(f"{message}{suffix}: ")

        if value == "" and default is not None:
            value = default
        if value == "" and not empty_ok:
            print("A value is required.")
            continue
        if validator is not None and not validator(value):
            print("Invalid value. Please try again.")
            continue
        return value


def confirm(message: str, *, default: bool = False) -> bool:
    """Prompt for a yes/no confirmation."""

    accepts = ("y", "yes")
    declines = ("n", "no")
    suffix = " [Y/n]" if default else " [y/N]"
    while True:
        answer = input(f"{message}{suffix}: ").strip().lower()
        if answer == "":
            return default
        if answer in accepts:
            return True
        if answer in declines:
            return False
        print("Please answer yes or no.")


def prompt_choice(message: str, choices: Sequence[str], *, default: str | None = None) -> str:
    """Prompt the user to choose one predefined option."""

    options = list(choices)
    if not options:
        raise ValueError("At least one choice is required.")
    labels = ", ".join(options)
    while True:
        suffix = f" [{default}]" if default is not None else ""
        answer = input(f"{message} ({labels}){suffix}: ").strip()
        if answer == "" and default is not None:
            return default
        if answer in options:
            return answer
        print("Choose one of the available options.")


def prompt_password(message: str) -> str:
    """Prompt the user for a secret value without echoing it."""

    return prompt(message, secret=True, empty_ok=False)
