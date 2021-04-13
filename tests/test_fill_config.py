from unittest import TestCase

from nx_config import fill_config, Config, ConfigSection


class FillConfigTestCase(TestCase):
    def test_fill_empty_config_no_input(self):
        _ = self

        class MyConfig(Config):
            pass

        cfg = MyConfig()
        fill_config(cfg)

    def test_fill_no_input(self):
        class MySection(ConfigSection):
            my_int: int = 42
            my_str: str = "Hello"

        class MySecondSection(ConfigSection):
            my_bool: bool = True

        class MyConfig(Config):
            first: MySection
            second: MySecondSection

        cfg = MyConfig()
        fill_config(cfg)

        self.assertEqual(cfg.first.my_int, 42)
        self.assertEqual(cfg.first.my_str, "Hello")
        self.assertEqual(cfg.second.my_bool, True)
