from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional
from unittest import TestCase
from uuid import UUID

from nx_config import (
    Config,
    ConfigSection,
    SecretString,
    URL,
    IncompleteSectionError,
    ParsingError,
)

# noinspection PyProtectedMember
from nx_config._core.fill_with_oracles import fill_config_w_oracles
from tests.typing_test_helpers import collection_type_holders


class FillConfigEnvOnlyTestCase(TestCase):
    def test_fill_empty_config(self):
        class MyConfig(Config):
            pass

        with self.subTest("Empty env_map"):
            fill_config_w_oracles(
                MyConfig(), in_stream=None, fmt=None, env_prefix=None, env_map={}
            )

        with self.subTest("Extra items in env_map"):
            fill_config_w_oracles(
                MyConfig(),
                in_stream=None,
                fmt=None,
                env_prefix=None,
                env_map={"a": "A", "b": "B"},
            )

    def test_fill_empty_section(self):
        class MySection(ConfigSection):
            pass

        class MyConfig(Config):
            my_section: MySection

        with self.subTest("Empty env_map"):
            fill_config_w_oracles(
                MyConfig(), in_stream=None, fmt=None, env_prefix=None, env_map={}
            )

        with self.subTest("Extra items in env_map"):
            fill_config_w_oracles(
                MyConfig(),
                in_stream=None,
                fmt=None,
                env_prefix=None,
                env_map={"a": "A", "b": "B"},
            )

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
        fill_config_w_oracles(
            cfg, in_stream=None, fmt=None, env_prefix=None, env_map={"a": "A"}
        )

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
                in_stream=None,
                fmt=None,
                env_prefix=None,
                env_map={
                    "a": "A",
                    "MY_OPT_STR": "Hello",  # Bad: No section
                    "MY_SEC1_MY_OPT_STR": "Hello",  # Bad: Single underscore between section and entry
                    "my_sec1__my_opt_str": "Hello",  # Bad: Lower case
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
        fill_config_w_oracles(
            cfg,
            in_stream=None,
            fmt=None,
            env_prefix=None,
            env_map={"MY_SECTION__MY_ENTRY": new_value},
        )

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
            in_stream=None,
            fmt=None,
            env_prefix=None,
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
            my_datetime: datetime = datetime(
                1955, 11, 5, 6, 15, 0, tzinfo=timezone(offset=timedelta(hours=-7))
            )
            my_uuid: UUID = UUID(int=987_654_321)
            my_path: Path = Path("/a/b/c/d.txt")
            my_secret: SecretString
            my_url: URL = "https://www.0123456789.com"

        class MySectionWOptionals(ConfigSection):
            my_int: Optional[int]
            my_float: Optional[float]
            my_bool: Optional[bool]
            my_str: Optional[str]
            my_datetime: Optional[datetime]
            my_uuid: Optional[UUID]
            my_path: Optional[Path]
            my_secret: Optional[SecretString]
            my_url: Optional[URL]

        class MySectionWOptionalsAndNones(ConfigSection):
            my_int: Optional[int] = None
            my_float: Optional[float] = None
            my_bool: Optional[bool] = None
            my_str: Optional[str] = None
            my_datetime: Optional[datetime] = None
            my_uuid: Optional[UUID] = None
            my_path: Optional[Path] = None
            my_secret: Optional[SecretString] = None
            my_url: Optional[URL] = None

        class MySectionWOptionalsAndDefaults(ConfigSection):
            my_int: Optional[int] = 42
            my_float: Optional[float] = 1.41999
            my_bool: Optional[bool] = True
            my_str: Optional[str] = "Yo"
            my_datetime: Optional[datetime] = datetime(
                1955, 11, 5, 6, 15, 0, tzinfo=timezone(offset=timedelta(hours=-7))
            )
            my_uuid: Optional[UUID] = UUID(int=987_654_321)
            my_path: Optional[Path] = Path("/a/b/c/d.txt")
            my_secret: Optional[SecretString]
            my_url: Optional[URL] = "https://www.0123456789.com"

        new_int_as_str = "101"
        new_float_as_str = "3.14"
        new_bool = False
        new_str = "Hello there!"
        new_datetime = datetime(
            2021, 5, 4, 1, 2, 3, tzinfo=timezone(offset=timedelta(hours=4))
        )
        new_uuid_as_str = "5f8ae2f4-906c-4d8d-9d61-69671117027e"
        new_path_as_str = "../some_dir/some_file.some_ext"
        new_secret = "abcd"
        new_url = "https://youtu.be/xvFZjo5PgG0"

        for section_class in (
            MySection,
            MySectionWDefaults,
            MySectionWOptionals,
            MySectionWOptionalsAndNones,
            MySectionWOptionalsAndDefaults,
        ):
            with self.subTest(section_class=section_class):

                class MyConfig(Config):
                    my_section: section_class

                cfg = MyConfig()
                fill_config_w_oracles(
                    cfg,
                    in_stream=None,
                    fmt=None,
                    env_prefix=None,
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
                fill_config_w_oracles(
                    cfg,
                    in_stream=None,
                    fmt=None,
                    env_prefix=None,
                    env_map={env_key: value_str},
                )
                self.assertEqual(True, cfg.my_section.my_entry)

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
                fill_config_w_oracles(
                    cfg,
                    in_stream=None,
                    fmt=None,
                    env_prefix=None,
                    env_map={env_key: value_str},
                )
                self.assertEqual(False, cfg.my_section.my_entry)

        for value_str in ("42", "tRUe", "zero", "Schrödinger's cat is dead", ""):
            with self.subTest("Invalid strings", value_str=value_str):
                with self.assertRaises(ParsingError) as ctx:
                    fill_config_w_oracles(
                        MyConfig(),
                        in_stream=None,
                        fmt=None,
                        env_prefix=None,
                        env_map={env_key: value_str},
                    )

                msg = str(ctx.exception)
                self.assertIn("'my_section'", msg)
                self.assertIn("'my_entry'", msg)
                self.assertIn(f"'{env_key}'", msg)
                self.assertIn("environment", msg.lower())
                self.assertIn(f"'{value_str}'", msg)
                self.assertIn("bool", msg.lower())

    def test_spaces_are_fine(self):
        class MySection(ConfigSection):
            first: str
            second: datetime
            third: Path
            fourth: SecretString

        class MyConfig(Config):
            sec: MySection

        cfg = MyConfig()

        new_str = " this is PeRfEcTlY   fine .  "
        new_datetime = datetime(1955, 11, 5, 6, 15, 0)
        new_path = Path("/this is a dir/ and this is a   file  .yaml")
        new_secret = "s a m e  h e r e"

        fill_config_w_oracles(
            cfg,
            in_stream=None,
            fmt=None,
            env_prefix=None,
            env_map={
                "SEC__FIRST": new_str,
                "SEC__SECOND": new_datetime.isoformat(sep=" "),
                "SEC__THIRD": str(new_path),
                "SEC__FOURTH": new_secret,
            },
        )

        self.assertEqual(new_str, cfg.sec.first)
        self.assertEqual(new_datetime, cfg.sec.second)
        self.assertEqual(new_path, cfg.sec.third)
        self.assertEqual(new_secret, cfg.sec.fourth)

    def test_datetimes_can_be_timezone_aware_or_naive(self):
        class MySection(ConfigSection):
            dt1: datetime
            dt2: datetime

        class MyConfig(Config):
            sec: MySection

        aware = datetime(2021, 5, 4, tzinfo=timezone(offset=timedelta(hours=8)))
        naive = datetime(2001, 1, 1)
        cfg = MyConfig()

        fill_config_w_oracles(
            cfg,
            in_stream=None,
            fmt=None,
            env_prefix=None,
            env_map={"SEC__DT1": aware.isoformat(), "SEC__DT2": naive.isoformat()},
        )
        self.assertEqual(aware, cfg.sec.dt1)
        self.assertEqual(naive, cfg.sec.dt2)

    def test_uuids_without_hyphens(self):
        class MySection(ConfigSection):
            my_uuid: UUID

        class MyConfig(Config):
            sec: MySection

        new_value = UUID("cb46fff2-5a46-4859-9eae-901d4fc33943")

        cfg = MyConfig()
        fill_config_w_oracles(
            cfg,
            in_stream=None,
            fmt=None,
            env_prefix=None,
            env_map={"SEC__MY_UUID": str(new_value).replace("-", "")},
        )

        self.assertEqual(new_value, cfg.sec.my_uuid)

    def test_invalid_int_str(self):
        class MySection(ConfigSection):
            my_entry: int

        class MyConfig(Config):
            my_section: MySection

        env_key = "MY_SECTION__MY_ENTRY"

        for value_str in ("", "3.14", "forty two"):
            with self.subTest("Invalid strings", value_str=value_str):
                with self.assertRaises(ParsingError) as ctx:
                    fill_config_w_oracles(
                        MyConfig(),
                        in_stream=None,
                        fmt=None,
                        env_prefix=None,
                        env_map={env_key: value_str},
                    )

                msg = str(ctx.exception)
                self.assertIn("'my_section'", msg)
                self.assertIn("'my_entry'", msg)
                self.assertIn(f"'{env_key}'", msg)
                self.assertIn("environment", msg.lower())
                self.assertIn(f"'{value_str}'", msg)
                self.assertIn("int", msg.lower())

    def test_invalid_float_str(self):
        class MySection(ConfigSection):
            my_entry: float

        class MyConfig(Config):
            my_section: MySection

        env_key = "MY_SECTION__MY_ENTRY"

        for value_str in ("", "pi", "True", "1.0.1"):
            with self.subTest("Invalid strings", value_str=value_str):
                with self.assertRaises(ParsingError) as ctx:
                    fill_config_w_oracles(
                        MyConfig(),
                        in_stream=None,
                        fmt=None,
                        env_prefix=None,
                        env_map={env_key: value_str},
                    )

                msg = str(ctx.exception)
                self.assertIn("'my_section'", msg)
                self.assertIn("'my_entry'", msg)
                self.assertIn(f"'{env_key}'", msg)
                self.assertIn("environment", msg.lower())
                self.assertIn(f"'{value_str}'", msg)
                self.assertIn("float", msg.lower())

    def test_invalid_datetime_str(self):
        class MySection(ConfigSection):
            my_entry: datetime

        class MyConfig(Config):
            my_section: MySection

        env_key = "MY_SECTION__MY_ENTRY"

        for value_str in ("", "today at noon", "2021-13-01 25:61:62"):
            with self.subTest("Invalid strings", value_str=value_str):
                with self.assertRaises(ParsingError) as ctx:
                    fill_config_w_oracles(
                        MyConfig(),
                        in_stream=None,
                        fmt=None,
                        env_prefix=None,
                        env_map={env_key: value_str},
                    )

                msg = str(ctx.exception)
                self.assertIn("'my_section'", msg)
                self.assertIn("'my_entry'", msg)
                self.assertIn(f"'{env_key}'", msg)
                self.assertIn("environment", msg.lower())
                self.assertIn(f"'{value_str}'", msg)
                self.assertIn("datetime", msg.lower())

    def test_invalid_uuid_str(self):
        class MySection(ConfigSection):
            my_entry: UUID

        class MyConfig(Config):
            my_section: MySection

        env_key = "MY_SECTION__MY_ENTRY"
        valid_str = str(UUID("cb46fff2-5a46-4859-9eae-901d4fc33943"))

        for value_str in ("", "42", valid_str.replace("f", "g"), valid_str[:-1]):
            with self.subTest("Invalid strings", value_str=value_str):
                with self.assertRaises(ParsingError) as ctx:
                    fill_config_w_oracles(
                        MyConfig(),
                        in_stream=None,
                        fmt=None,
                        env_prefix=None,
                        env_map={env_key: value_str},
                    )

                msg = str(ctx.exception)
                self.assertIn("'my_section'", msg)
                self.assertIn("'my_entry'", msg)
                self.assertIn(f"'{env_key}'", msg)
                self.assertIn("environment", msg.lower())
                self.assertIn(f"'{value_str}'", msg)
                self.assertIn("uuid", msg.lower())

    def test_can_parse_collections(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    int_tuple: tps.tuple[int, ...]
                    int_set: tps.frozenset[int]
                    float_tuple: tps.tuple[float, ...]
                    float_set: tps.frozenset[float]
                    bool_tuple: tps.tuple[bool, ...]
                    bool_set: tps.frozenset[bool]
                    str_tuple: tps.tuple[str, ...]
                    str_set: tps.frozenset[str]
                    datetime_tuple: tps.tuple[datetime, ...]
                    datetime_set: tps.frozenset[datetime]
                    uuid_tuple: tps.tuple[UUID, ...]
                    uuid_set: tps.frozenset[UUID]
                    path_tuple: tps.tuple[Path, ...]
                    path_set: tps.frozenset[Path]
                    secret_tuple: tps.tuple[SecretString, ...]
                    secret_set: tps.frozenset[SecretString]
                    url_tuple: tps.tuple[URL, ...]
                    url_set: tps.frozenset[URL]

                class MyConfig(Config):
                    sec: MySection

                cfg = MyConfig()

                expected = {
                    "int_tuple": ("  1, 2, 3  ,    42 ,-5", (1, 2, 3, 42, -5)),
                    "int_set": (
                        "  1, 2, 3  ,2,    42 ,-5",
                        frozenset((1, 2, 3, 42, -5)),
                    ),
                    "float_tuple": (
                        "1,   2.2, 3.14   ,0,0.001,  -9  ",
                        (1.0, 2.2, 3.14, 0.0, 0.001, -9.0),
                    ),
                    "float_set": (
                        "1,   2.2, 3.14   ,0,1,0.001,  -9  ",
                        frozenset((1.0, 2.2, 3.14, 0.0, 0.001, -9.0)),
                    ),
                    "bool_tuple": (
                        " True, 0   , No,Yes,on, ON  ",
                        (True, False, False, True, True, True),
                    ),
                    "bool_set": (
                        " True, 0   , No,Yes,on, ON  ",
                        frozenset((True, False)),
                    ),
                    "str_tuple": (
                        "Hello, wörld!  ,foO,,baR    ",
                        ("Hello", "wörld!", "foO", "", "baR"),
                    ),
                    "str_set": (
                        "Hello, wörld!  ,hello,   ,,baR    ",
                        frozenset(("Hello", "wörld!", "hello", "", "baR")),
                    ),
                    "datetime_tuple": (
                        "2021-05-04T06:15:00+01:00,2001-11-1 5:12:9,    1982-1-1 00:00:00+00:00    ",
                        (
                            datetime(
                                2021,
                                5,
                                4,
                                6,
                                15,
                                tzinfo=timezone(offset=timedelta(hours=1)),
                            ),
                            datetime(2001, 11, 1, 5, 12, 9),
                            datetime(1982, 1, 1, tzinfo=timezone.utc),
                        ),
                    ),
                    "datetime_set": (
                        "2001-11-01T05:12:09.0000,2021-05-04T06:15:00+01:00,2001-11-1 5:12:9,1982-1-1 00:00:00+00:00",
                        frozenset(
                            (
                                datetime(
                                    2021,
                                    5,
                                    4,
                                    6,
                                    15,
                                    tzinfo=timezone(offset=timedelta(hours=1)),
                                ),
                                datetime(2001, 11, 1, 5, 12, 9),
                                datetime(1982, 1, 1, tzinfo=timezone.utc),
                            )
                        ),
                    ),
                    "uuid_tuple": (
                        (
                            "c544d643-5db3-452b-8594-4042b01b21fb,"
                            "  \tc31a9e10-fb5e-4b99-8689-5e9017121bad\t,"
                            "   72fa850e62a04ae38e704e9e14b6bd49 "
                        ),
                        (
                            UUID("c544d643-5db3-452b-8594-4042b01b21fb"),
                            UUID("c31a9e10-fb5e-4b99-8689-5e9017121bad"),
                            UUID("72fa850e-62a0-4ae3-8e70-4e9e14b6bd49"),
                        ),
                    ),
                    "uuid_set": (
                        (
                            "72fa850e-62a0-4ae3-8e70-4e9e14b6bd49,"
                            "c544d643-5db3-452b-8594-4042b01b21fb,"
                            "  \tc31a9e10-fb5e-4b99-8689-5e9017121bad\t,"
                            "   72fa850e62a04ae38e704e9e14b6bd49 "
                        ),
                        frozenset(
                            (
                                UUID("c544d643-5db3-452b-8594-4042b01b21fb"),
                                UUID("c31a9e10-fb5e-4b99-8689-5e9017121bad"),
                                UUID("72fa850e-62a0-4ae3-8e70-4e9e14b6bd49"),
                            )
                        ),
                    ),
                    "path_tuple": (
                        "\t\t /a/b/c.d  \n  , .., g, ../e/../../f,g,..    \n",
                        (
                            Path("/a/b/c.d"),
                            Path(".."),
                            Path("g"),
                            Path("../e/../../f"),
                            Path("g"),
                            Path(".."),
                        ),
                    ),
                    "path_set": (
                        "\t\t /a/b/c.d  \n  , .., g, ../e/../../f,g,..    \n",
                        frozenset(
                            (
                                Path("/a/b/c.d"),
                                Path(".."),
                                Path("g"),
                                Path("../e/../../f"),
                            )
                        ),
                    ),
                    "secret_tuple": (
                        "Hello, wörld!  ,foO,,baR    ",
                        ("Hello", "wörld!", "foO", "", "baR"),
                    ),
                    "secret_set": (
                        "Hello, wörld!  ,hello,   ,,baR    ",
                        frozenset(("Hello", "wörld!", "hello", "", "baR")),
                    ),
                    "url_tuple": (
                        "www.a.b, http://127.0.0.1:2222   , huh?whah=ok",
                        ("www.a.b", "http://127.0.0.1:2222", "huh?whah=ok"),
                    ),
                    "url_set": (
                        "www.a.b, http://127.0.0.1:2222   ,f,f,f, huh?whah=ok      ,f",
                        frozenset(
                            ("www.a.b", "http://127.0.0.1:2222", "f", "huh?whah=ok")
                        ),
                    ),
                }

                fill_config_w_oracles(
                    cfg,
                    in_stream=None,
                    fmt=None,
                    env_prefix=None,
                    env_map={f"SEC__{k.upper()}": v[0] for k, v in expected.items()},
                )

                for k, v in expected.items():
                    self.assertEqual(v[1], getattr(cfg.sec, k), msg=k)

    def test_can_parse_single_element_collections(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    int_tuple: tps.tuple[int, ...]
                    int_set: tps.frozenset[int]
                    float_tuple: tps.tuple[float, ...]
                    float_set: tps.frozenset[float]
                    bool_tuple: tps.tuple[bool, ...]
                    bool_set: tps.frozenset[bool]
                    str_tuple: tps.tuple[str, ...]
                    str_set: tps.frozenset[str]
                    datetime_tuple: tps.tuple[datetime, ...]
                    datetime_set: tps.frozenset[datetime]
                    uuid_tuple: tps.tuple[UUID, ...]
                    uuid_set: tps.frozenset[UUID]
                    path_tuple: tps.tuple[Path, ...]
                    path_set: tps.frozenset[Path]
                    secret_tuple: tps.tuple[SecretString, ...]
                    secret_set: tps.frozenset[SecretString]
                    url_tuple: tps.tuple[URL, ...]
                    url_set: tps.frozenset[URL]

                class MyConfig(Config):
                    sec: MySection

                cfg = MyConfig()

                expected = {
                    "int_tuple": ("    42 ", (42,)),
                    "int_set": ("    42 ", frozenset((42,))),
                    "float_tuple": ("3.14", (3.14,)),
                    "float_set": ("3.14", frozenset((3.14,))),
                    "bool_tuple": ("Yes", (True,)),
                    "bool_set": ("0 ", frozenset((False,))),
                    "str_tuple": ("foO", ("foO",)),
                    "str_set": ("baR    ", frozenset(("baR",))),
                    "datetime_tuple": (
                        "1982-1-1 00:00:00+00:00",
                        (datetime(1982, 1, 1, tzinfo=timezone.utc),),
                    ),
                    "datetime_set": (
                        "1982-1-1 00:00:00",
                        frozenset((datetime(1982, 1, 1),)),
                    ),
                    "uuid_tuple": (
                        "c544d643-5db3-452b-8594-4042b01b21fb",
                        (UUID("c544d643-5db3-452b-8594-4042b01b21fb"),),
                    ),
                    "uuid_set": (
                        "c544d643-5db3-452b-8594-4042b01b21fb",
                        frozenset((UUID("c544d643-5db3-452b-8594-4042b01b21fb"),)),
                    ),
                    "path_tuple": ("/a/b/c.d  \n   \n", (Path("/a/b/c.d"),)),
                    "path_set": ("\t\t /a/b/c.d ", frozenset((Path("/a/b/c.d"),))),
                    "secret_tuple": ("foO", ("foO",)),
                    "secret_set": ("Hello   ", frozenset(("Hello",))),
                    "url_tuple": ("http://127.0.0.1:2222", ("http://127.0.0.1:2222",)),
                    "url_set": (
                        " http://127.0.0.1:2222",
                        frozenset(("http://127.0.0.1:2222",)),
                    ),
                }

                fill_config_w_oracles(
                    cfg,
                    in_stream=None,
                    fmt=None,
                    env_prefix=None,
                    env_map={f"SEC__{k.upper()}": v[0] for k, v in expected.items()},
                )

                for k, v in expected.items():
                    self.assertEqual(v[1], getattr(cfg.sec, k), msg=k)

    def test_invalid_element_str_in_collection(self):
        for tp, value_str, invalid, base_str in (
            (tp, value_str, invalid, base_str)
            for base, value_str, invalid, base_str in (
                (int, "  1, 2, 3  ,2,    forty two ,-5", "forty two", "int"),
                (int, ",  1, 2, 3  ,2,    42 ,-5", "", "int"),
                (int, "  1, 2, 3  ,2,    42 ,-5,", "", "int"),
                (int, "1.111", "1.111", "int"),
                (float, "1,   2.2, pi   ,0,1,0.001,  -9  ", "pi", "float"),
                (
                    bool,
                    " True, 0   , No,Yes,on, Schrödinger's cat is dead",
                    "Schrödinger's cat is dead",
                    "bool",
                ),
                (
                    datetime,
                    "2001-11-41T05:12:09,2021-05-04T06:15:00+01:00",
                    "2001-11-41T05:12:09",
                    "datetime",
                ),
                (
                    UUID,
                    "72fa850e-62a0-4ae3-8e70-4e9e14b6bd49, abc, 72fa850e62a04ae38e704e9e14b6bd49 ",
                    "abc",
                    "UUID",
                ),
            )
            for tps in collection_type_holders
            for tp in (tps.tuple[base, ...], tps.frozenset[base])
        ):
            with self.subTest(type=tp, value_str=value_str):

                class MySection(ConfigSection):
                    my_entry: tp

                class MyConfig(Config):
                    my_section: MySection

                env_key = "MY_SECTION__MY_ENTRY"

                with self.assertRaises(ParsingError) as ctx:
                    fill_config_w_oracles(
                        MyConfig(),
                        in_stream=None,
                        fmt=None,
                        env_prefix=None,
                        env_map={env_key: value_str},
                    )

                msg = str(ctx.exception)
                self.assertIn("'my_section'", msg)
                self.assertIn("'my_entry'", msg)
                self.assertIn(f"'{env_key}'", msg)
                self.assertIn("environment", msg.lower())
                self.assertIn(f"'{value_str}'", msg)
                self.assertIn(f"'{invalid}'", msg)
                self.assertIn(f"{base_str.lower()}", msg.lower())

    def test_empty_str_for_collections(self):
        for tp, expected in (
            (tp, expected)
            for tps in collection_type_holders
            for base in (int, float, bool, str, datetime, UUID, Path, SecretString, URL)
            for tp, expected in (
                (tps.tuple[base, ...], ()),
                (tps.frozenset[base], frozenset()),
            )
        ):
            with self.subTest(type=tp, expected=expected):

                class MySection(ConfigSection):
                    my_entry: tp

                class MyConfig(Config):
                    my_section: MySection

                cfg = MyConfig()
                fill_config_w_oracles(
                    cfg,
                    in_stream=None,
                    fmt=None,
                    env_prefix=None,
                    env_map={"MY_SECTION__MY_ENTRY": ""},
                )
                self.assertEqual(expected, cfg.my_section.my_entry)

    def test_optional_types_can_be_set(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    int_op: Optional[int]
                    float_op: Optional[float] = None
                    bool_op: Optional[bool] = True
                    str_tuple_op: Optional[tps.tuple[str, ...]]
                    str_tuple_op2: Optional[tps.tuple[str, ...]] = None
                    datetime_tuple_op: Optional[tps.tuple[datetime, ...]] = None
                    uuid_tuple_op: Optional[tps.tuple[UUID, ...]] = ()
                    uuid_tuple_op2: Optional[tps.tuple[UUID, ...]] = ()
                    bool_nop: bool = False
                    path_tuple_op: Optional[tps.tuple[Path, ...]] = (
                        Path("/a"),
                        Path("/b.c"),
                    )
                    secret_set_op: Optional[tps.frozenset[SecretString]]
                    url_set_op: Optional[tps.frozenset[URL]] = None
                    bool_tuple: tps.tuple[bool, ...]
                    int_set_op: Optional[tps.frozenset[int]] = frozenset()
                    float_set_op: Optional[tps.frozenset[float]] = frozenset(
                        (3.100, 31.00, 310.0)
                    )
                    float_set_op2: Optional[tps.frozenset[float]] = frozenset(
                        (3.100, 31.00, 310.0)
                    )

                class MyConfig(Config):
                    sec: MySection

                cfg = MyConfig()

                expected = {
                    "int_op": ("42", 42),
                    "float_op": ("1.21", 1.21),
                    "bool_op": ("false", False),
                    "str_tuple_op": (
                        "Hello, wörld!  ,foO,,baR    ",
                        ("Hello", "wörld!", "foO", "", "baR"),
                    ),
                    "datetime_tuple_op": (
                        "2021-05-04T06:15:00+01:00,2001-11-1 5:12:9,    1982-1-1 00:00:00+00:00    ",
                        (
                            datetime(
                                2021,
                                5,
                                4,
                                6,
                                15,
                                tzinfo=timezone(offset=timedelta(hours=1)),
                            ),
                            datetime(2001, 11, 1, 5, 12, 9),
                            datetime(1982, 1, 1, tzinfo=timezone.utc),
                        ),
                    ),
                    "uuid_tuple_op": (
                        (
                            "c544d643-5db3-452b-8594-4042b01b21fb,"
                            "  \tc31a9e10-fb5e-4b99-8689-5e9017121bad\t,"
                            "   72fa850e62a04ae38e704e9e14b6bd49 "
                        ),
                        (
                            UUID("c544d643-5db3-452b-8594-4042b01b21fb"),
                            UUID("c31a9e10-fb5e-4b99-8689-5e9017121bad"),
                            UUID("72fa850e-62a0-4ae3-8e70-4e9e14b6bd49"),
                        ),
                    ),
                    "bool_nop": ("Yes", True),
                    "path_tuple_op": (
                        "\t\t /a/b/c.d  \n  , .., g, ../e/../../f,g,..    \n",
                        (
                            Path("/a/b/c.d"),
                            Path(".."),
                            Path("g"),
                            Path("../e/../../f"),
                            Path("g"),
                            Path(".."),
                        ),
                    ),
                    "secret_set_op": (
                        "Hello, wörld!  ,hello,   ,,baR    ",
                        frozenset(("Hello", "wörld!", "hello", "", "baR")),
                    ),
                    "url_set_op": (
                        "www.a.b, http://127.0.0.1:2222   ,f,f,f, huh?whah=ok      ,f",
                        frozenset(
                            ("www.a.b", "http://127.0.0.1:2222", "f", "huh?whah=ok")
                        ),
                    ),
                    "bool_tuple": (
                        " True, 0   , No,Yes,on, ON  ",
                        (True, False, False, True, True, True),
                    ),
                    "int_set_op": (
                        "  1, 2, 3  ,2,    42 ,-5",
                        frozenset((1, 2, 3, 42, -5)),
                    ),
                    "float_set_op": (
                        "1,   2.2, 3.14   ,0,1,0.001,  -9  ",
                        frozenset((1.0, 2.2, 3.14, 0.0, 0.001, -9.0)),
                    ),
                }

                fill_config_w_oracles(
                    cfg,
                    in_stream=None,
                    fmt=None,
                    env_prefix=None,
                    env_map={f"SEC__{k.upper()}": v[0] for k, v in expected.items()},
                )

                for k, v in expected.items():
                    self.assertEqual(v[1], getattr(cfg.sec, k), msg=k)

                self.assertEqual(MyConfig().sec.str_tuple_op2, cfg.sec.str_tuple_op2)
                self.assertEqual(MyConfig().sec.uuid_tuple_op2, cfg.sec.uuid_tuple_op2)
                self.assertEqual(MyConfig().sec.float_set_op2, cfg.sec.float_set_op2)

    def test_empty_str_for_optional_types(self):
        for tp in (
            tp
            for tps in collection_type_holders
            for tp in (
                int,
                float,
                bool,
                str,
                Path,
                SecretString,
                URL,
                tps.tuple[int, ...],
                tps.tuple[UUID, ...],
                tps.tuple[str, ...],
                tps.frozenset[float],
                tps.frozenset[datetime],
                tps.frozenset[str],
                tps.tuple[Path, ...],
                tps.frozenset[Path],
                tps.tuple[SecretString, ...],
                tps.frozenset[SecretString],
                tps.tuple[URL, ...],
                tps.frozenset[URL],
            )
        ):
            with self.subTest(type=tp):

                class MySection(ConfigSection):
                    my_entry: Optional[tp]

                class MyConfig(Config):
                    my_section: MySection

                cfg = MyConfig()
                fill_config_w_oracles(
                    cfg,
                    in_stream=None,
                    fmt=None,
                    env_prefix=None,
                    env_map={"MY_SECTION__MY_ENTRY": ""},
                )
                self.assertIsNone(cfg.my_section.my_entry)

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

                fill_config_w_oracles(
                    cfg,
                    in_stream=None,
                    fmt=None,
                    env_prefix=None,
                    env_map={
                        "SEC__E_STR": "",
                        "SEC__E_OPT_INT": "",
                        "SEC__E_OPT_STR": "",
                        "SEC__E_TUPLE_INT": "",
                        "SEC__E_TUPLE_STR": "",
                        "SEC__E_OPT_TUPLE_INT": "",
                        "SEC__E_OPT_TUPLE_STR": "",
                    },
                )

                self.assertEqual("", cfg.sec.e_str)
                self.assertIsNone(cfg.sec.e_opt_int)
                self.assertIsNone(cfg.sec.e_opt_str)
                self.assertEqual((), cfg.sec.e_tuple_int)
                self.assertEqual((), cfg.sec.e_tuple_str)
                self.assertIsNone(cfg.sec.e_opt_tuple_int)
                self.assertIsNone(cfg.sec.e_opt_tuple_str)

    def test_custom_env_vars_prefix(self):
        class MySection(ConfigSection):
            my_entry: int

        class MyConfig(Config):
            my_section: MySection

        env_var = "MY_SECTION__MY_ENTRY"
        prefix = "CU5T0M_PR3F1X"
        no_prefix_value = 101
        prefix_value = no_prefix_value + 1

        env_map = {
            env_var: str(no_prefix_value),
            f"{prefix}__{env_var}": str(prefix_value),
        }

        cfg1 = MyConfig()
        fill_config_w_oracles(
            cfg1, in_stream=None, fmt=None, env_prefix=None, env_map=env_map
        )
        self.assertEqual(no_prefix_value, cfg1.my_section.my_entry)

        cfg2 = MyConfig()
        fill_config_w_oracles(
            cfg2, in_stream=None, fmt=None, env_prefix=prefix, env_map=env_map
        )
        self.assertEqual(prefix_value, cfg2.my_section.my_entry)
