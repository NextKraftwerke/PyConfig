from argparse import ArgumentParser
from typing import Type, Optional

from nx_config.config import Config

_base_cli_path_option = "config-path"
_path_metavar = _base_cli_path_option.upper().replace("-", "_")


def add_cli_options(parser: ArgumentParser, *, prefix: Optional[str] = None, config_t: Type[Config]):
    parser.add_argument(
        f"--{_base_cli_path_option}" if prefix is None else f"--{prefix}-{_base_cli_path_option}",
        type=str,
        help=f"Path to configuration file. Target python class: {config_t.__name__}.",
        metavar=_path_metavar,
    )
