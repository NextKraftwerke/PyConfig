from argparse import Namespace
from pathlib import Path
from typing import Mapping, Optional

from nx_config.cli import _base_cli_path_option, _check_prefix

_base_cli_option = _base_cli_path_option.replace("-", "_")
_base_env_key = _base_cli_option.upper()


def resolve_path_w_oracles(
    prefix: Optional[str],
    cli_args: Optional[Namespace],
    env_map: Mapping[str, str],
) -> Optional[Path]:
    if prefix is None:
        cli_option = _base_cli_option
        env_key = _base_env_key
    else:
        _check_prefix(prefix, purpose="resolution")
        prefix = prefix.replace("-", "_")
        cli_option = f"{prefix}_{_base_cli_option}"
        env_key = f"{prefix.upper()}_{_base_env_key}"

    if cli_args is not None:
        try:
            cli_value = getattr(cli_args, cli_option)
        except AttributeError as xcp:
            raise AttributeError(
                f"Argument 'cli_args' is expected to be an 'argparser.Namespace' and have an attribute '{cli_option}'"
                f" (whose value may be None, if this option was not used in the command-line)."
            ) from xcp

        if cli_value is not None:
            return Path(cli_value)

    try:
        return Path(env_map[env_key])
    except KeyError:
        return None
