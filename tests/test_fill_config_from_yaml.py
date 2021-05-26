from datetime import datetime, timezone, timedelta
from inspect import cleandoc
from io import StringIO
from pathlib import Path
from typing import TextIO, Optional
from unittest import TestCase
from uuid import UUID

from yaml import YAMLError
from yaml.constructor import ConstructorError

from nx_config import ConfigSection, Config, Format, SecretString, URL
# noinspection PyProtectedMember
from nx_config._core.fill_with_oracles import fill_config_w_oracles


def _in(s: str) -> TextIO:
    return StringIO(cleandoc(s))


def _fill_in(cfg: Config, s: str):
    fill_config_w_oracles(cfg, in_stream=_in(s), fmt=Format.yaml, env_prefix=None, env_map={})


class FillFromYAMLTestCase(TestCase):
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

    def test_set_to_none(self):
        class MySection(ConfigSection):
            entry1: Optional[int] = 42
            entry2: Optional[UUID] = UUID(int=42)

        class MyConfig(Config):
            sec: MySection

        cfg = MyConfig()
        _fill_in(
            cfg,
            """
            sec:
              entry1:
              entry2: 
            """,
        )

        self.assertIsNone(cfg.sec.entry1)
        self.assertIsNone(cfg.sec.entry2)

    def test_set_native_yaml_types(self):
        class MySection(ConfigSection):
            e_int1: int
            e_int2: int
            e_float1: float
            e_float2: float
            e_bool1: bool
            e_bool2: bool
            e_str1: str
            e_str2: str
            e_str3: Optional[str]
            e_str4: Optional[str]
            e_datetime1: datetime
            e_datetime2: datetime
            e_datetime3: datetime
            e_datetime4: datetime

        class MyConfig(Config):
            sec: MySection

        cfg = MyConfig()
        _fill_in(
            cfg,
            """
            sec:
              e_int1: 42
              e_int2: -42
              e_float1: 3.14
              e_float2: -3.14
              e_bool1: false
              e_bool2: true
              e_str1: Hello, world!
              e_str2: "  Goodbye, Dave  "
              e_str3: ""
              e_str4: 
              e_datetime1: 2021-5-4 9:15:00.000009+05:00
              e_datetime2: 2021-05-04T09:15:00.000009-05:00
              e_datetime3: 2021-5-4 9:15:00.000009
              e_datetime4: 2021-5-4 9:15:00Z
            """,
        )

        self.assertEqual(42, cfg.sec.e_int1)
        self.assertEqual(-42, cfg.sec.e_int2)
        self.assertEqual(3.14, cfg.sec.e_float1)
        self.assertEqual(-3.14, cfg.sec.e_float2)
        self.assertFalse(cfg.sec.e_bool1)
        self.assertTrue(cfg.sec.e_bool2)
        self.assertEqual("Hello, world!", cfg.sec.e_str1)
        self.assertEqual("  Goodbye, Dave  ", cfg.sec.e_str2)
        self.assertEqual("", cfg.sec.e_str3)
        self.assertIsNone(cfg.sec.e_str4)
        self.assertEqual(datetime(2021, 5, 4, 9, 15, 0, 9, tzinfo=timezone(timedelta(hours=5))), cfg.sec.e_datetime1)
        self.assertEqual(datetime(2021, 5, 4, 9, 15, 0, 9, tzinfo=timezone(timedelta(hours=-5))), cfg.sec.e_datetime2)
        self.assertEqual(datetime(2021, 5, 4, 9, 15, 0, 9), cfg.sec.e_datetime3)
        self.assertEqual(datetime(2021, 5, 4, 9, 15, tzinfo=timezone.utc), cfg.sec.e_datetime4)

    def test_set_secret(self):
        class MySection(ConfigSection):
            entry: SecretString

        class MyConfig(Config):
            sec: MySection

        cfg = MyConfig()
        _fill_in(
            cfg,
            """
            sec:
              entry: abcdef123
            """,
        )

        self.assertEqual("abcdef123", cfg.sec.entry)

    def test_set_url(self):
        class MySection(ConfigSection):
            entry: URL

        class MyConfig(Config):
            sec: MySection

        cfg = MyConfig()
        _fill_in(
            cfg,
            """
            sec:
              entry: www.a.b.c
            """,
        )

        self.assertEqual("www.a.b.c", cfg.sec.entry)

    def test_set_path(self):
        class MySection(ConfigSection):
            entry: Path

        class MyConfig(Config):
            sec: MySection

        cfg = MyConfig()
        _fill_in(
            cfg,
            """
            sec:
              entry: /a/b/c.txt
            """,
        )

        self.assertEqual(Path("/a/b/c.txt"), cfg.sec.entry)

    def test_set_uuid(self):
        class MySection(ConfigSection):
            entry: UUID

        class MyConfig(Config):
            sec: MySection

        new_value = UUID("29e7a5cb-7eb6-45c2-b86d-2707db2c3f46")

        cfg = MyConfig()
        _fill_in(
            cfg,
            f"""
            sec:
              entry: {new_value}
            """,
        )

        self.assertEqual(new_value, cfg.sec.entry)

    def test_wrong_type_no_collection(self):
        for t, value in (
            (int, 3.14),
            (float, 42),
            (str, 42),
            (str, datetime(2021, 5, 4, 9, 15)),
            (datetime, 1622026088),
            (bool, "0"),
            (UUID, 42),
            (int, [1, 2, 3]),
            (SecretString, True),
            (URL, -1),
        ):
            with self.subTest(type=t, value=value):
                class MySection(ConfigSection):
                    my_entry: t

                class MyConfig(Config):
                    my_section: MySection

                value_str = f"\"{value}\"" if isinstance(value, str) else str(value)

                with self.assertRaises(TypeError) as ctx:
                    _fill_in(
                        MyConfig(),
                        f"""
                        my_section:
                          my_entry: {value_str}
                        """,
                    )

                msg = str(ctx.exception)
                self.assertIn("'my_section'", msg)
                self.assertIn("'my_entry'", msg)
                self.assertIn(t.__name__, msg)
                self.assertIn(type(value).__name__, msg)

    def test_invalid_uuid_str_no_collection(self):
        class MySection(ConfigSection):
            my_entry: UUID

        class MyConfig(Config):
            my_section: MySection

        invalid = "1234-abcd"
        with self.assertRaises(ValueError) as ctx:
            _fill_in(
                MyConfig(),
                f"""
                my_section:
                  my_entry: {invalid}
                """,
            )

        msg = str(ctx.exception)
        self.assertIn("'my_section'", msg)
        self.assertIn("'my_entry'", msg)
        self.assertIn(f"'{invalid}'", msg)
        self.assertIn("UUID", msg)

    # tuple (old and new)
    # frozenset (old and new)
    # wrong collection type
    # wrong element type
    # invalid collection syntax
    # invalid for conversion to element in collection
    # dict
    # int for str
    # optional collection (to none, to empty, to some)
    # optional tuple[str] (to none, to empty, to some, to single empty, whitespace)
    # validates
    # all entries must be set
    # env takes precedence
    # Uset _set to get error messages!
