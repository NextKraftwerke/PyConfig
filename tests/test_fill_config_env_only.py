from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional
from unittest import TestCase
from uuid import UUID

from nx_config import Config, ConfigSection, SecretString, URL, IncompleteSectionError, ParsingError
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

    def test_overwrite_str(self):
        class MySection(ConfigSection):
            my_entry: str = "nothing"

        class MyConfig(Config):
            my_section: MySection

        new_value = "something"
        cfg = MyConfig()
        fill_config_w_oracles(cfg, env_map={"MY_SECTION__MY_ENTRY": new_value})

        self.assertEqual(new_value, cfg.my_section.my_entry)

    def test_fill_int(self):
        class MySection(ConfigSection):
            my_entry1: int
            my_entry2: int = 42

        class MyConfig(Config):
            my_section: MySection

        new_value1 = "101"
        new_value2 = "708"
        cfg = MyConfig()
        fill_config_w_oracles(
            cfg,
            env_map={
                "MY_SECTION__MY_ENTRY1": new_value1,
                "MY_SECTION__MY_ENTRY2": new_value2,
            },
        )

        self.assertEqual(int(new_value1), cfg.my_section.my_entry1)
        self.assertEqual(int(new_value2), cfg.my_section.my_entry2)

    def test_fill_all_base_types(self):
        class MySection(ConfigSection):
            my_int: int
            my_float: float
            my_bool: bool
            my_str: str
            my_datetime: datetime
            my_uuid: UUID
            my_path: Path
            my_secret: SecretString
            my_url: URL

        class MySectionWDefaults(ConfigSection):
            my_int: int = 42
            my_float: float = 1.41999
            my_bool: bool = True
            my_str: str = "Yo"
            my_datetime: datetime = datetime(1955, 11, 5, 6, 15, 0, tzinfo=timezone(offset=timedelta(hours=-7)))
            my_uuid: UUID = UUID(int=987_654_321)
            my_path: Path = Path("/a/b/c/d.txt")
            my_secret: SecretString
            my_url: URL = "https://www.0123456789.com"

        new_int_as_str = "101"
        new_float_as_str = "3.14"
        new_bool = False
        new_str = "Hello there!"
        new_datetime = datetime(2021, 5, 4, 1, 2, 3, tzinfo=timezone(offset=timedelta(hours=4)))
        new_uuid_as_str = "5f8ae2f4-906c-4d8d-9d61-69671117027e"
        new_path_as_str = "../some_dir/some_file.some_ext"
        new_secret = "abcd"
        new_url = "https://youtu.be/xvFZjo5PgG0"

        for section_class in (MySection, MySectionWDefaults):
            with self.subTest(section_class=section_class):
                class MyConfig(Config):
                    my_section: section_class

                cfg = MyConfig()
                fill_config_w_oracles(
                    cfg,
                    env_map={
                        "MY_SECTION__MY_INT": new_int_as_str,
                        "MY_SECTION__MY_FLOAT": new_float_as_str,
                        "MY_SECTION__MY_BOOL": str(new_bool),
                        "MY_SECTION__MY_STR": new_str,
                        "MY_SECTION__MY_DATETIME": new_datetime.isoformat(sep="T"),
                        "MY_SECTION__MY_UUID": new_uuid_as_str,
                        "MY_SECTION__MY_PATH": new_path_as_str,
                        "MY_SECTION__MY_SECRET": new_secret,
                        "MY_SECTION__MY_URL": new_url,
                    },
                )

                self.assertEqual(int(new_int_as_str), cfg.my_section.my_int)
                self.assertEqual(float(new_float_as_str), cfg.my_section.my_float)
                self.assertEqual(new_bool, cfg.my_section.my_bool)
                self.assertEqual(new_str, cfg.my_section.my_str)
                self.assertEqual(new_datetime, cfg.my_section.my_datetime)
                self.assertEqual(UUID(new_uuid_as_str), cfg.my_section.my_uuid)
                self.assertEqual(Path(new_path_as_str), cfg.my_section.my_path)
                self.assertEqual(new_secret, cfg.my_section.my_secret)
                self.assertEqual(new_url, cfg.my_section.my_url)

    def test_fill_boolean_from_string(self):
        class MySection(ConfigSection):
            my_entry: bool

        class MyConfig(Config):
            my_section: MySection

        env_key = "MY_SECTION__MY_ENTRY"

        for value_str in ("True", "true", "TRUE", "Yes", "yes", "YES", "On", "on", "ON", "1"):
            with self.subTest("Truey strings", value_str=value_str):
                cfg = MyConfig()
                fill_config_w_oracles(cfg, env_map={env_key: value_str})
                self.assertEqual(True, cfg.my_section.my_entry)

        for value_str in ("False", "false", "FALSE", "No", "no", "NO", "Off", "off", "OFF", "0"):
            with self.subTest("Falsey strings", value_str=value_str):
                cfg = MyConfig()
                fill_config_w_oracles(cfg, env_map={env_key: value_str})
                self.assertEqual(False, cfg.my_section.my_entry)

        for value_str in ("42", "tRUe", "zero", ""):
            with self.subTest("Invalid strings", value_str=value_str):
                with self.assertRaises(ParsingError) as ctx:
                    fill_config_w_oracles(MyConfig(), env_map={env_key: value_str})

                msg = str(ctx.exception)
                self.assertIn("'my_section'", msg)
                self.assertIn("'my_entry'", msg)
                self.assertIn(f"'{env_key}'", msg)
                self.assertIn("environment", msg.lower())
                self.assertIn(f"'{value_str}'", msg)
                self.assertIn("bool", msg.lower())

    # TODO:
    #   - spaces in strings
    #   - spaces in datetimes
    #   - spaces in paths
    #   - Windows-style paths
    #   - UUIDs without hyphens
    #   - invalid strings for each base type
    #   - tuples
    #   - frozensets
    #   - optionals
    #   - one really complex case
    #   - document restrictions
    #   - One big complex test with the actual fill_config
    #   - Which exceptions do we want?
    #     - Invalid type-hint?
    #     - Wrong type value (default or from yaml)?
    #     - Default secret?
    #     - Wrong class syntax?
    #
