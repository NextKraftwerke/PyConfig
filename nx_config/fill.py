from os import environ
from typing import Optional

# noinspection PyProtectedMember
from nx_config._core.fill_with_oracles import fill_config_w_oracles as _fill_config_w_oracles
from nx_config.config import Config


def fill_config(cfg: Config, *, env_prefix: Optional[str] = None):
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
    return _fill_config_w_oracles(cfg, env_prefix=env_prefix, env_map=environ)
