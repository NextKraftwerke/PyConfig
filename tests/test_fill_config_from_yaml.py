from inspect import cleandoc
from io import StringIO
from typing import TextIO, Optional
from unittest import TestCase

from yaml import YAMLError
from yaml.constructor import ConstructorError

from nx_config import ConfigSection, Config, Format
# noinspection PyProtectedMember
from nx_config._core.fill_with_oracles import fill_config_w_oracles


def _in(s: str) -> TextIO:
    return StringIO(cleandoc(s))


def _fill_in(cfg: Config, s: str):
    fill_config_w_oracles(cfg, in_stream=_in(s), fmt=Format.yaml, env_prefix=None, env_map={})


class FillFromYAMLTestCase(TestCase):
    def test_not_setting_entry(self):
        class MySection(ConfigSection):
            entry1: int = 0
            entry2: int = 0

        class MyConfig(Config):
            sec: MySection

        cfg = MyConfig()
        _fill_in(
            cfg,
            """
            sec:
              entry2: 42
            """,
        )

        self.assertEqual(0, cfg.sec.entry1)
        self.assertEqual(42, cfg.sec.entry2)

    def test_set_to_none(self):
        class MySection(ConfigSection):
            entry: Optional[int] = 42

        class MyConfig(Config):
            sec: MySection

        cfg = MyConfig()
        _fill_in(
            cfg,
            """
            sec:
              entry:
            """,
        )

        self.assertIsNone(cfg.sec.entry)

    def test_cannot_load_dangerous_code_from_yaml(self):
        class MyConfig(Config):
            pass

        with self.assertRaises(ConstructorError):
            _fill_in(
                MyConfig(),
                """
                !!python/object/new:os.system [echo EXPLODE WORLD!]
                """,
            )

    def test_invalid_yaml_syntax(self):
        class MyConfig(Config):
            pass

        with self.assertRaises(YAMLError):
            _fill_in(
                MyConfig(),
                """
                ]
                """,
            )

    def test_empty_file(self):
        class MySection(ConfigSection):
            entry: int = 42

        class MyConfig(Config):
            sec: MySection

        cfg = MyConfig()
        _fill_in(
            cfg,
            """
            """,
        )
        self.assertEqual(42, cfg.sec.entry)

    def test_not_setting_section(self):
        class MySection(ConfigSection):
            entry: int = 0

        class MyConfig(Config):
            sec1: MySection
            sec2: MySection

        cfg = MyConfig()
        _fill_in(
            cfg,
            """
            sec1:
              entry: 42
            """,
        )

        self.assertEqual(42, cfg.sec1.entry)
        self.assertEqual(0, cfg.sec2.entry)
