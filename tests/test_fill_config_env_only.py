from typing import Optional
from unittest import TestCase

from nx_config import Config, ConfigSection, IncompleteSectionError
# noinspection PyProtectedMember
from nx_config._core.fill_with_oracles import fill_config_w_oracles


class FillConfigEnvOnlyTestCase(TestCase):
    def test_fill_empty_config(self):
        class MyConfig(Config):
            pass

        with self.subTest("Empty env_map"):
            fill_config_w_oracles(MyConfig(), env_map={})

        with self.subTest("Extra items in env_map"):
            fill_config_w_oracles(MyConfig(), env_map={"a": "A", "b": "B"})

    def test_fill_empty_section(self):
        class MySection(ConfigSection):
            pass

        class MyConfig(Config):
            my_section: MySection

        with self.subTest("Empty env_map"):
            fill_config_w_oracles(MyConfig(), env_map={})

        with self.subTest("Extra items in env_map"):
            fill_config_w_oracles(MyConfig(), env_map={"a": "A", "b": "B"})

    def test_fill_already_full_empty_env_map(self):
        class MySection1(ConfigSection):
            my_int: int = 42
            my_opt_str: Optional[str] = None

        class MySection2(ConfigSection):
            my_bool: bool = True

        class MyConfig(Config):
            my_sec1: MySection1
            my_sec2: MySection2

        cfg = MyConfig()
        fill_config_w_oracles(cfg, env_map={"a": "A"})

        self.assertEqual(42, cfg.my_sec1.my_int)
        self.assertEqual(None, cfg.my_sec1.my_opt_str)
        self.assertEqual(True, cfg.my_sec2.my_bool)

    def test_missing_entries_after_fill(self):
        class MySection1(ConfigSection):
            my_int: int = 42
            my_opt_str: Optional[str]

        class MySection2(ConfigSection):
            my_bool: bool = True

        class MyConfig(Config):
            my_sec1: MySection1
            my_sec2: MySection2

        with self.assertRaises(IncompleteSectionError) as ctx:
            fill_config_w_oracles(
                MyConfig(),
                env_map={
                    "a": "A",
                    "MY_OPT_STR": "Hello",              # Bad: No section
                    "MY_SEC1_MY_OPT_STR": "Hello",      # Bad: Single underscore between section and entry
                    "my_sec1__my_opt_str": "Hello",     # Bad: Lower case
                },
            )

        msg = str(ctx.exception)
        self.assertIn("'my_sec1'", msg)
        self.assertIn("'my_opt_str'", msg)

    def test_fill_str(self):
        class MySection(ConfigSection):
            my_str: str = "nothing"

        class MyConfig(Config):
            my_section: MySection

        something = "something"
        cfg = MyConfig()
        fill_config_w_oracles(cfg, env_map={"MY_SECTION__MY_STR": something})

        self.assertEqual(something, cfg.my_section.my_str)
