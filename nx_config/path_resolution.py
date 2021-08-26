from argparse import Namespace
from os import environ
from pathlib import Path
from typing import Optional

# noinspection PyProtectedMember
from nx_config._core.path_with_oracles import resolve_path_w_oracles as _resolve_path_w_oracles


def resolve_config_path(prefix: Optional[str] = None, *, cli_args: Optional[Namespace] = None) -> Optional[Path]:
    """
    TODO: incl.: Document precedence between env var and CLI arg.

    :param prefix:
    :param cli_args:
    :return:
    """
    # WARNING: This function is difficult to test because testing would involve
    #   setting environment variables (which remain set from test to test),
    #   or mocking and patching 'environ' (which is messy).
    #   So instead we test the internal function resolve_path_w_oracles which allows
    #   the injection of any necessary input sources.
    #   Testing this internal function is enough as long as resolve_config_path is only a
    #   very, very thin wrapper around it, but not if resolve_config_path starts using a lot
    #   of additional logic. So please keep this a simple one-liner and make any
    #   necessary changes directly to resolve_path_w_oracles instead of here.
    #     Thanks!
    return _resolve_path_w_oracles(prefix=prefix, cli_args=cli_args, env_map=environ)
