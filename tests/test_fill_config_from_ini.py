from configparser import Error as ConfigParserError
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Mapping
from unittest import TestCase
from uuid import UUID

from nx_config import (
    ConfigSection,
    Config,
    Format,
    SecretString,
    URL,
    validate,
    ValidationError,
    IncompleteSectionError,
)
from tests.fill_test_helpers import fill_from_str
from tests.typing_test_helpers import collection_type_holders


def _fill_in(cfg: Config, s: str, *, env_map: Optional[Mapping[str, str]] = None):
    fill_from_str(cfg, s, Format.ini, env_map)


class FillFromINITestCase(TestCase):
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
            [sec1]
            entry=42
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
            [sec]
            entry2= 42
            """,
        )

        self.assertEqual(0, cfg.sec.entry1)
        self.assertEqual(42, cfg.sec.entry2)

    def test_invalid_ini_syntax(self):
        class MyConfig(Config):
            pass

        with self.assertRaises(ConfigParserError):
            _fill_in(
                MyConfig(),
                """
                foo=1
                """,
            )

        with self.assertRaises(ConfigParserError):
            _fill_in(
                MyConfig(),
                """
                [foo]
                bar=2
                [buzz
                """,
            )

        with self.assertRaises(ConfigParserError):
            _fill_in(
                MyConfig(),
                """
                [foo]
                bar=2
                [foo]
                buzz=3
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

    def test_extra_ini_ignored(self):
        class MySection(ConfigSection):
            entry: int = 42

        class MyConfig(Config):
            sec: MySection

        cfg = MyConfig()
        _fill_in(
            cfg,
            """
            [other]
            e1: 51
            e2: 99
            [sec]
            entry: 13
            other: 7
            """,
        )
        self.assertEqual(13, cfg.sec.entry)

    def test_ultimate_empty_str_input(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    e_str: str = "a"
                    e_opt_int: Optional[int] = 0
                    e_opt_str: Optional[str] = "a"
                    e_tuple_int: tps.tuple[int, ...] = (0,)
                    e_tuple_str: tps.tuple[str, ...] = ("a",)
                    e_opt_tuple_int: Optional[tps.tuple[int, ...]] = (0,)
                    e_opt_tuple_str: Optional[tps.tuple[str, ...]] = ("a",)

                class MyConfig(Config):
                    sec: MySection

                cfg = MyConfig()
                _fill_in(
                    cfg,
                    """
                    [sec]
                    e_str=
                    e_opt_int=
                    e_opt_str=
                    e_tuple_int=
                    e_tuple_str=
                    e_opt_tuple_int=
                    e_opt_tuple_str=
                    """,
                )

                self.assertEqual("", cfg.sec.e_str)
                self.assertIsNone(cfg.sec.e_opt_int)
                self.assertIsNone(cfg.sec.e_opt_str)
                self.assertEqual((), cfg.sec.e_tuple_int)
                self.assertEqual((), cfg.sec.e_tuple_str)
                self.assertIsNone(cfg.sec.e_opt_tuple_int)
                self.assertIsNone(cfg.sec.e_opt_tuple_str)

    def test_fill_boolean_from_string(self):
        class MySection(ConfigSection):
            a_parameter: bool

        class MyConfig(Config):
            some_section: MySection

        for value_str in (
            "True",
            "true",
            "TRUE",
            "Yes",
            "yes",
            "YES",
            "On",
            "on",
            "ON",
            "1",
        ):
            with self.subTest("Truey strings", value_str=value_str):
                cfg = MyConfig()
                _fill_in(
                    cfg,
                    f"""
                    [some_section]
                    a_parameter = {value_str}
                    """,
                )
                self.assertEqual(True, cfg.some_section.a_parameter)

        for value_str in (
            "False",
            "false",
            "FALSE",
            "No",
            "no",
            "NO",
            "Off",
            "off",
            "OFF",
            "0",
        ):
            with self.subTest("Falsey strings", value_str=value_str):
                cfg = MyConfig()
                _fill_in(
                    cfg,
                    f"""
                    [some_section]
                    a_parameter = {value_str}
                    """,
                )
                self.assertEqual(False, cfg.some_section.a_parameter)

        for value_str in ("42", "tRUe", "zero", "Schrödinger's cat is dead", ""):
            with self.subTest("Invalid strings", value_str=value_str):
                with self.assertRaises(ValueError) as ctx:
                    _fill_in(
                        cfg,
                        f"""
                        [some_section]
                        a_parameter = {value_str}
                        """,
                    )

                msg = str(ctx.exception)
                self.assertIn("'some_section'", msg)
                self.assertIn("'a_parameter'", msg)
                self.assertIn(f"'{value_str}'", msg)
                self.assertIn("bool", msg.lower())

    def test_set_simple_types(self):
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
            e_str5: Optional[str]
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
            [sec]
            e_int1 = 42
            e_int2 = -42
            e_float1 = 3.14
            e_float2 = -3.14
            e_bool1 = false
            e_bool2 = true
            e_str1 =        Hello, world!         \t\t  
            e_str2 = "  Goodbye, Dave  "
            e_str3 = ""
            e_str4 =
            e_str5 = foo-be-doo
            e_datetime1 = 2021-5-4 9:15:00.000009+05:00
            e_datetime2 = 2021-05-04T09:15:00.000009-05:00
            e_datetime3 = 2021-5-4 9:15:00.000009
            e_datetime4 = 2021-5-4 9:15:00Z
            """,
        )

        self.assertEqual(42, cfg.sec.e_int1)
        self.assertEqual(-42, cfg.sec.e_int2)
        self.assertEqual(3.14, cfg.sec.e_float1)
        self.assertEqual(-3.14, cfg.sec.e_float2)
        self.assertFalse(cfg.sec.e_bool1)
        self.assertTrue(cfg.sec.e_bool2)
        self.assertEqual("Hello, world!", cfg.sec.e_str1)
        self.assertEqual('"  Goodbye, Dave  "', cfg.sec.e_str2)
        self.assertEqual('""', cfg.sec.e_str3)
        self.assertIsNone(cfg.sec.e_str4)
        self.assertEqual("foo-be-doo", cfg.sec.e_str5)
        self.assertEqual(
            datetime(2021, 5, 4, 9, 15, 0, 9, tzinfo=timezone(timedelta(hours=5))),
            cfg.sec.e_datetime1,
        )
        self.assertEqual(
            datetime(2021, 5, 4, 9, 15, 0, 9, tzinfo=timezone(timedelta(hours=-5))),
            cfg.sec.e_datetime2,
        )
        self.assertEqual(datetime(2021, 5, 4, 9, 15, 0, 9), cfg.sec.e_datetime3)
        self.assertEqual(
            datetime(2021, 5, 4, 9, 15, tzinfo=timezone.utc), cfg.sec.e_datetime4
        )

    def test_set_secret(self):
        class MySection(ConfigSection):
            entry: SecretString

        class MyConfig(Config):
            sec: MySection

        cfg = MyConfig()
        _fill_in(
            cfg,
            """
            [sec]
            entry = abcdef123
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
            [sec]
            
            entry: www.a.b.c
            """,
        )

        self.assertEqual("www.a.b.c", cfg.sec.entry)

    def test_set_path(self):
        class MySection(ConfigSection):
            entry1: Path
            entry2: Path

        class MyConfig(Config):
            sec: MySection

        p1 = "/a/b/c.txt"
        p2 = "..   this  also   / works..  klmnb"

        cfg = MyConfig()
        _fill_in(
            cfg,
            f"""
            [sec]
              entry1: {p1}
              entry2 = {p2}
            """,
        )

        self.assertEqual(Path(p1), cfg.sec.entry1)
        self.assertEqual(Path(p2), cfg.sec.entry2)

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
            [sec]
            entry = {new_value}
            """,
        )

        self.assertEqual(new_value, cfg.sec.entry)

    def test_wrong_type_no_collection(self):
        for t, value_str in (
            (int, "3.14"),
            (float, "true"),
            (datetime, "1622026088"),
            (bool, '"0"'),
            (UUID, "42"),
            (int, "1,2,3"),
        ):
            with self.subTest(type=t, value_str=value_str):

                class MySection(ConfigSection):
                    my_entry: t

                class MyConfig(Config):
                    my_section: MySection

                with self.assertRaises(ValueError) as ctx:
                    _fill_in(
                        MyConfig(),
                        f"""
                        [my_section]
                        my_entry = {value_str}
                        """,
                    )

                msg = str(ctx.exception)
                self.assertIn("'my_section'", msg)
                self.assertIn("'my_entry'", msg)
                self.assertIn("str", msg)
                self.assertIn(value_str, msg)
                self.assertIn(t.__name__, msg)

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
                [my_section]
                my_entry: {invalid}
                """,
            )

        msg = str(ctx.exception)
        self.assertIn("'my_section'", msg)
        self.assertIn("'my_entry'", msg)
        self.assertIn(f"'{invalid}'", msg)
        self.assertIn("UUID", msg)

    def test_set_collections(self):
        uuid1 = UUID("ab35dd93-4c8b-485f-b6cd-ba6a6b29daff")
        uuid2 = UUID("d7717fc6-6faa-43a1-b640-675de3115592")
        dt1 = datetime(2021, 5, 4, 9, 15, 14, 111_003)
        dt2 = datetime(2001, 7, 6, tzinfo=timezone.utc)
        secret = "I did nothing last summer"

        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    int_tuple: tps.tuple[int, ...]
                    bool_tuple: tps.tuple[bool, ...] = ()
                    uuid_tuple: tps.tuple[UUID, ...]
                    str_tuple: tps.tuple[str, ...] = ("one", "two", "three")
                    path_tuple: tps.tuple[Path, ...]
                    float_set: tps.frozenset[float] = frozenset()
                    url_set: tps.frozenset[URL] = frozenset(("default.url.com",))
                    datetime_set: tps.frozenset[datetime]
                    secret_set: tps.frozenset[SecretString] = frozenset()

                class MyConfig(Config):
                    sec: MySection

                cfg = MyConfig()
                _fill_in(
                    cfg,
                    f"""
                    [sec]
                    int_tuple: 3, 7, 1
                    bool_tuple: true,false,  no ,ON
                    uuid_tuple={uuid1},{uuid2}
                    str_tuple:
                    path_tuple= /a/b/c.txt
                    float_set: 3.14, 4.2, 0.0, 0.0, 0.0
                    url_set=
                    datetime_set = {dt1}, {dt2}
                    secret_set = {secret}
                    """,
                )

                self.assertEqual((3, 7, 1), cfg.sec.int_tuple)
                self.assertEqual((True, False, False, True), cfg.sec.bool_tuple)
                self.assertEqual((uuid1, uuid2), cfg.sec.uuid_tuple)
                self.assertEqual((), cfg.sec.str_tuple)
                self.assertEqual((Path("/a/b/c.txt"),), cfg.sec.path_tuple)
                self.assertEqual(frozenset((3.14, 0.0, 4.2)), cfg.sec.float_set)
                self.assertEqual(frozenset(), cfg.sec.url_set)
                self.assertEqual(frozenset((dt1, dt2)), cfg.sec.datetime_set)
                self.assertEqual(frozenset((secret,)), cfg.sec.secret_set)

    def test_wrong_element_type(self):
        t = collection_type_holders[0].tuple

        class MySection(ConfigSection):
            an_entry: t[int, ...] = ()

        class MyConfig(Config):
            a_sec: MySection

        with self.assertRaises(ValueError) as ctx:
            _fill_in(
                MyConfig(),
                """
                [a_sec]
                an_entry: 42, foo, 37
                """,
            )

        msg = str(ctx.exception)
        self.assertIn("'an_entry'", msg)
        self.assertIn("'a_sec'", msg)
        self.assertIn("tuple[int, ...]", msg.lower())

    def test_invalid_uuid_str_in_collection(self):
        t = collection_type_holders[0].tuple

        class MySection(ConfigSection):
            my_entry: t[UUID, ...]

        class MyConfig(Config):
            my_section: MySection

        invalid = "boohoo-di-bapp"

        with self.assertRaises(ValueError) as ctx:
            _fill_in(
                MyConfig(),
                f"""
                [my_section]
                my_entry:4d31b561-89a6-4a5b-a55f-b22e1eb94c22, {invalid}, 1128c5b9-af97-4081-a71d-acceff2e2817
                """,
            )

        msg = str(ctx.exception)
        self.assertIn("'my_section'", msg)
        self.assertIn("'my_entry'", msg)
        self.assertIn(f"'{invalid}'", msg)
        self.assertIn("UUID", msg)

    def test_fill_from_ini_validates(self):
        expected_msg = " 31 hhjo e 833 lkjh f    124popp9990 . .."

        class MySection(ConfigSection):
            entry: int

            @validate
            def fail(self):
                raise ValueError(expected_msg)

        class MyConfig(Config):
            a_sec: MySection

        with self.assertRaises(ValidationError) as ctx:
            _fill_in(
                MyConfig(),
                """
                [a_sec]
                entry = 42
                """,
            )

        msg = str(ctx.exception)
        self.assertIn("'a_sec'", msg)
        self.assertIn(expected_msg, msg)

    def test_all_entries_must_be_set(self):
        class MySection(ConfigSection):
            an_entry: int
            another: int

        class MyConfig(Config):
            a_sec: MySection

        with self.assertRaises(IncompleteSectionError) as ctx:
            _fill_in(
                MyConfig(),
                """
                [a_sec]
                an_entry = 42
                """,
            )

        msg = str(ctx.exception)
        self.assertIn("'a_sec'", msg)
        self.assertIn("'another'", msg)

    def test_env_takes_precedence(self):
        class MySection(ConfigSection):
            entry: SecretString

        class MyConfig(Config):
            sec: MySection

        cfg = MyConfig()
        env_wins = "ENV wins!"
        _fill_in(
            cfg,
            """
            [sec]
            entry = INI wins!
            """,
            env_map={"SEC__ENTRY": env_wins},
        )

        self.assertEqual(env_wins, cfg.sec.entry)

    def test_optional_collection(self):
        t = collection_type_holders[0].tuple
        fs = collection_type_holders[0].frozenset

        class MySection(ConfigSection):
            entry: Optional[t[Path, ...]] = ()
            other: Optional[fs[float]]
            otherer: Optional[t[int, ...]] = None

        class MyConfig(Config):
            sec: MySection

        with self.subTest("To none"):
            cfg1 = MyConfig()
            _fill_in(
                cfg1,
                """
                [sec]
                  entry=
                  other = \t
                  otherer:
                """,
            )
            self.assertIsNone(cfg1.sec.entry)
            self.assertIsNone(cfg1.sec.other)
            self.assertIsNone(cfg1.sec.otherer)

        with self.subTest("To some"):
            cfg2 = MyConfig()
            _fill_in(
                cfg2,
                """
                [sec]
                  entry: a
                  other: 5,6.7
                  otherer: 5,6,7
                """,
            )
            self.assertEqual((Path("a"),), cfg2.sec.entry)
            self.assertEqual(frozenset((5.0, 6.7)), cfg2.sec.other)
            self.assertEqual((5, 6, 7), cfg2.sec.otherer)

    def test_optional_str_collection(self):
        t = collection_type_holders[0].tuple
        fs = collection_type_holders[0].frozenset

        class MySection(ConfigSection):
            e1: Optional[t[str, ...]]
            e2: Optional[t[str, ...]]
            e3: Optional[t[str, ...]]
            e4: Optional[fs[str]]
            e5: Optional[fs[str]]
            e6: Optional[fs[str]]

        class MyConfig(Config):
            sec: MySection

        cfg = MyConfig()

        _fill_in(
            cfg,
            """
            [sec]
            e1:
            e2: ,
            e3: a, bb , ccc
            e4:
            e5: ,
            e6: a, bb , ccc
            """,
        )

        self.assertIsNone(cfg.sec.e1)
        self.assertEqual(("", ""), cfg.sec.e2)
        self.assertEqual(("a", "bb", "ccc"), cfg.sec.e3)
        self.assertIsNone(cfg.sec.e4)
        self.assertEqual(frozenset(("", "")), cfg.sec.e5)
        self.assertEqual(frozenset(("a", "bb", "ccc")), cfg.sec.e6)
