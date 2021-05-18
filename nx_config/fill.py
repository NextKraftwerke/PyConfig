from os import environ, PathLike
from pathlib import Path
from typing import Optional, Union

# noinspection PyProtectedMember
from nx_config._core.fill_with_oracles import fill_config_w_oracles as _fill_config_w_oracles
from nx_config.config import Config

_supported_extensions = (".yaml", ".yml", ".YAML", ".YML")


def fill_config(cfg: Config, *, path: Optional[Union[str, PathLike]] = None, env_prefix: Optional[str] = None):
    # WARNING: This function is difficult to test because testing would involve
    #   using lots of config files as resources and actually reading them, plus
    #   setting lots of environment variables (which remain set from test to test),
    #   or mocking and patching these kinds of things (which is messy).
    #   So instead we test the internal function fill_config_w_oracles which allows
    #   the injection of any necessary input sources.
    #   Testing this internal function is enough as long as fill_config is only a
    #   very, very thin wrapper around it, but not if fill_config starts using a lot
    #   of additional logic. So please keep this a simple one-liner and make any
    #   necessary changes directly to fill_config_w_oracles instead of here.
    #     Thanks!
    if path is None:
        return _fill_config_w_oracles(cfg, in_stream=None, env_prefix=env_prefix, env_map=environ)

    if not isinstance(path, Path):
        path = Path(path)

    dot_ext = path.suffix
    if dot_ext not in _supported_extensions:
        raise ValueError(
            f"Configuration filepath '{path}' has unsupported extension. This version of PyConfig supports"
            f" the formats YAML (extensions: {', '.join(_supported_extensions)})."
        )

    with path.open() as fstream:
        return _fill_config_w_oracles(cfg, in_stream=fstream, env_prefix=env_prefix, env_map=environ)
