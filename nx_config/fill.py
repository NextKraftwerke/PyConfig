from os import environ, PathLike
from pathlib import Path
from typing import Optional, TextIO, Union

# noinspection PyProtectedMember
from nx_config._core.fill_with_oracles import fill_config_w_oracles as _fill_config_w_oracles
from nx_config.config import Config
from nx_config.format import Format

_supported_yaml_extensions = (".yaml", ".yml", ".YAML", ".YML")
_supported_ini_extensions = (".ini", ".INI")


def fill_config(
    cfg: Config,
    *,
    stream: Optional[TextIO] = None,
    fmt: Optional[Format] = None,
    env_prefix: Optional[str] = None,
):
    """
    TODO: incl.: Document that env takes precedence over config files and that if an env var is present,
        it must be a valid value (will not fallback to config file in case of invalid env var) and
        the corresponding value in the config file (if any) will not be used and therefore will not
        be validated. So an invalid entry in a config file might go unnoticed if it is overriden by
        an env var.
        Also: Document restrictions with env. vars and ini, incl.:
        - No strings/secrets with commas in collections
        - No strings/secrets with surrounding spaces in collections
        - env. vars only: Surrounding whitespace is kept for base types but not for single-element collections
        - ini only: Surrounding whitespace is trimmed for all types
        Also: Document behaviour when empty strings are given as input from INI or environment variables:
        | Typ | `"" -> ??` |
        | --- | --- |
        | `int, float, bool, UUID, datetime` | `ValueError` |
        | `str, SecretString, URL` | `""` |
        | `Path` | `Path("")` |
        | `Optional[base_or_collection]` | `None` |
        | `tuple[base, ...]` | `()` |
        | `frozenset[base]` | `frozenset()` |

    :param cfg:
    :param stream:
    :param fmt:
    :param env_prefix:
    """
    # WARNING: This function is difficult to test because testing would involve
    #   setting lots of environment variables (which remain set from test to test),
    #   or mocking and patching 'environ' (which is messy).
    #   So instead we test the internal function fill_config_w_oracles which allows
    #   the injection of any necessary input sources.
    #   Testing this internal function is enough as long as fill_config is only a
    #   very, very thin wrapper around it, but not if fill_config starts using a lot
    #   of additional logic. So please keep this a simple one-liner and make any
    #   necessary changes directly to fill_config_w_oracles instead of here.
    #     Thanks!
    return _fill_config_w_oracles(cfg, in_stream=stream, fmt=fmt, env_prefix=env_prefix, env_map=environ)


def fill_config_from_path(
    cfg: Config,
    *,
    path: Optional[Union[str, PathLike]] = None,
    env_prefix: Optional[str] = None,
):
    """
    TODO: incl.: Refer to docs from fill_config

    :param cfg:
    :param path:
    :param env_prefix:
    """
    # WARNING: This function is difficult to test because testing would involve
    #   setting lots of environment variables (which remain set from test to test),
    #   or mocking and patching 'environ' (which is messy), plus actually using lots of
    #   config files as test resources and actually opening them during testing, or
    #   mocking and patching 'open' (which is terribly messy).
    #   Since this is only a very thin convenience wrapper around fill_config (which is only
    #   a very thin wrapper around fill_config_w_oracles, which is thoroughly tested), it's
    #   okay. But only if it stays that way! So please keep this as simple as possible and make
    #   any necessary changes directly to fill_config_w_oracles instead of here.
    #     Thanks!
    if path is None:
        return fill_config(cfg, env_prefix=env_prefix)

    if not isinstance(path, Path):
        path = Path(path)

    if path.is_dir():
        raise IsADirectoryError(f"Is a directory: '{path}'")

    dot_ext = path.suffix

    if dot_ext in _supported_yaml_extensions:
        fmt = Format.yaml
    elif dot_ext in _supported_ini_extensions:
        fmt = Format.ini
    else:
        raise ValueError(
            f"Configuration filepath '{path}' has unsupported extension. This version of PyConfig supports"
            f" the formats YAML (extensions: {', '.join(_supported_yaml_extensions)}) and INI (extensions:"
            f" {', '.join(_supported_ini_extensions)})."
        )

    with path.open() as fstream:
        return fill_config(cfg, stream=fstream, fmt=fmt, env_prefix=env_prefix)
