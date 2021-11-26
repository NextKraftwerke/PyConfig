import sys
from argparse import ArgumentParser, Action
from typing import Type, Optional

# noinspection PyProtectedMember
from nx_config._core.generate_template import generate_template as _generate_template
from nx_config.config import Config
from nx_config.format import Format

_base_cli_path_option = "config-path"
_base_cli_generate_option = "generate-config"
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
    """
    TODO: incl.: Document each individual CLI option.
        Also: When documenting config-path and generate-config, refer to the docs of fill_config (e.g. on the
        limitations of INI and env vars).

    :param parser:
    :param prefix:
    :param config_t:
    """
    if prefix is None:
        path_option = f"--{_base_cli_path_option}"
        generate_option = f"--{_base_cli_generate_option}"
    else:
        _check_prefix(prefix, purpose="option")
        path_option = f"--{prefix}-{_base_cli_path_option}"
        generate_option = f"--{prefix}-{_base_cli_generate_option}"

    parser.add_argument(
        path_option,
        type=str,
        help=f"Path to configuration file. Target python class: {config_t.__name__}.",
        metavar="CONFIG_PATH",
    )

    class _GenerateConfigAction(Action):
        def __call__(self, action_parser, namespace, value, option_string=None):
            fmt = getattr(Format, value)
            _generate_template(config_t, fmt, sys.stdout)
            action_parser.exit(0)

    parser.add_argument(
        generate_option,
        type=str,
        choices=tuple(x.name for x in Format),
        help=(
            f"Generate a template configuration file in the specified format,"
            f" print it to the standard output and exit. Target python class: {config_t.__name__}."
        ),
        action=_GenerateConfigAction,
    )
