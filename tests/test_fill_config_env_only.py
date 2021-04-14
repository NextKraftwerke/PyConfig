from unittest import TestCase

from nx_config import Config
# noinspection PyProtectedMember
from nx_config._core.fill_with_oracles import fill_config_w_oracles


class FillConfigEnvOnlyTestCase(TestCase):
    def test_fill_empty_config_empty_env_map(self):
        _ = self

        class MyConfig1(Config):
            pass

        cfg = MyConfig1()
        fill_config_w_oracles(cfg, env_map={})
