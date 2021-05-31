from argparse import ArgumentParser
from typing import Type, Optional

from nx_config.config import Config

_base_cli_path_option = "config-path"
_path_metavar = _base_cli_path_option.upper().replace("-", "_")
_lower_ascii_letters = "abcdefghijklmnopqrstuvwxyz"
_upper_ascii_letters = _lower_ascii_letters.upper()
_digits = "0123456789"
_prefix_first_char = _lower_ascii_letters + _upper_ascii_letters
_prefix_chars = _prefix_first_char + _digits + "-_"


def _check_prefix(prefix: str, purpose: str):
    if prefix == "":
        raise ValueError(
            f"Invalid empty prefix for configuration path {purpose}. If you don't want to use a custom"
            f" prefix, use None instead (default)."
        )

    if (prefix[0] not in _prefix_first_char) or any(x not in _prefix_chars for x in prefix[1:]):
        raise ValueError(
            f"Invalid prefix {repr(prefix)} for configuration path {purpose}. The only characters"
            f" allowed in the prefix are lower case ASCII letters '{_lower_ascii_letters}', upper case"
            f" ASCII letters '{_lower_ascii_letters.upper()}', numerical digits '{_digits}', dashes '-'"
            f" and underscores '_', with the additional restriction that the first character must be a letter."
        )


def add_cli_options(parser: ArgumentParser, *, prefix: Optional[str] = None, config_t: Type[Config]):
    if prefix is None:
        path_option = f"--{_base_cli_path_option}"
    else:
        _check_prefix(prefix, purpose="option")
        path_option = f"--{prefix}-{_base_cli_path_option}"

    parser.add_argument(
        path_option,
        type=str,
        help=f"Path to configuration file. Target python class: {config_t.__name__}.",
        metavar=_path_metavar,
    )
