from inspect import cleandoc
from io import StringIO
from typing import Optional, Mapping

from nx_config import Config, Format

# noinspection PyProtectedMember
from nx_config._core.fill_with_oracles import fill_config_w_oracles


def fill_from_str(
    cfg: Config, s: str, fmt: Format, env_map: Optional[Mapping[str, str]]
):
    if env_map is None:
        env_map = {}
    fill_config_w_oracles(
        cfg, in_stream=StringIO(cleandoc(s)), fmt=fmt, env_prefix=None, env_map=env_map
    )
