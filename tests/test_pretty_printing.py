from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional
from unittest import TestCase
from uuid import UUID

from nx_config import ConfigSection, URL, SecretString, validate, Config
from nx_config.test_utils import update_section
from tests.typing_test_helpers import collection_type_holders, CollectionTypeHolder


def _get_testing_section_cls(tps: CollectionTypeHolder) -> type:
    # noinspection PyUnresolvedReferences
    class DatabaseSection(ConfigSection):
        user: str = "John Doe"
        password: SecretString
        token: UUID = UUID(int=5_444_333_222_111)
        birthday: datetime = datetime(
            1955, 11, 5, 1, 22, tzinfo=timezone(offset=timedelta(hours=-3))
        )
        url: URL = "www.nx_config_db.com"
        port: int = 1_234
        ultimate_question: Optional[str] = None
        no_collection: Optional[tps.tuple[int, ...]] = None
        resources: Path = Path("/a/b/c/resources/")
        rel_resources: Path = Path("c/resources")
        secure_mode: bool = True
        growth_factor: float = 1.5
        cats: Optional[tps.frozenset[str]] = frozenset(
            ("grey", "brown", "black", "white")
        )
        dogs: tps.tuple[str, ...] = ("lazy", "happy", "sad")
        sasquatch: tps.tuple[str, ...] = ()
        big_foot: tps.frozenset[str] = frozenset()
        secret_files: tps.frozenset[Path] = frozenset(
            (Path("hi.txt"), Path("/hello.md"))
        )
        more_files: tps.tuple[Path, ...] = (Path("bye.exe"), Path("/see_ya.py"))
        fibonacci: tps.frozenset[int] = frozenset((0, 1, 1, 2, 3, 5))
        more_fibonacci: tps.tuple[int, ...] = (8, 13, 21, 34)
        holidays: tps.frozenset[datetime] = frozenset((datetime(1985, 11, 12),))
        non_holidays: tps.tuple[datetime, ...] = (datetime(1985, 11, 13),)
        old_tokens: tps.frozenset[UUID] = frozenset(
            (UUID(int=1), UUID(int=9_999_999_999_999))
        )
        future_tokens: tps.tuple[UUID, ...] = (UUID(int=2), UUID(int=7), UUID(int=17))
        needs_escaping: str = "Hello\nWorld\r!\tHowdy?"

        class Nested:
            pass

        Alias = Nested

        def a_method(self):
            pass

        @validate
        def a_validator(self):
            pass

    return DatabaseSection


class EmptySection(ConfigSection):
    pass


def _get_big_testing_config_cls(tps: CollectionTypeHolder) -> type:
    db_section = _get_testing_section_cls(tps)

    class BigConfig(Config):
        database: db_section
        empty: EmptySection

    return BigConfig


class EmptyConfig(Config):
    pass


def indent_after_newline(s: str) -> str:
    return s.replace("\n", "\n    ")


class PrettyPrintingTestCase(TestCase):
    def setUp(self) -> None:
        db_section_cls = _get_testing_section_cls(collection_type_holders[0])
        database_sec = db_section_cls()

        cats_str = "{" + ", ".join(f"'{x}'" for x in database_sec.cats) + "}"
        dogs_str = "(" + ", ".join(f"'{x}'" for x in database_sec.dogs) + ")"
        big_foot_str = "{}"
        secret_files_str = (
            "{" + ", ".join(f"'{x}'" for x in database_sec.secret_files) + "}"
        )
        more_files_str = (
            "(" + ", ".join(f"'{x}'" for x in database_sec.more_files) + ")"
        )
        holidays_str = "{" + ", ".join(str(x) for x in database_sec.holidays) + "}"
        non_holidays_str = (
            "(" + ", ".join(str(x) for x in database_sec.non_holidays) + ")"
        )
        old_tokens_str = "{" + ", ".join(str(x) for x in database_sec.old_tokens) + "}"
        future_tokens_str = (
            "(" + ", ".join(str(x) for x in database_sec.future_tokens) + ")"
        )
        needs_escaping_str = "Hello\\nWorld\\r!\\tHowdy?"

        self.expected_database_str = (
            f"DatabaseSection(user='{database_sec.user}',"
            f" password=Unset,"
            f" token={database_sec.token},"
            f" birthday={database_sec.birthday},"
            f" url='{database_sec.url}',"
            f" port={database_sec.port},"
            f" ultimate_question=None,"
            f" no_collection=None,"
            f" resources='{database_sec.resources}',"
            f" rel_resources='{database_sec.rel_resources}',"
            f" secure_mode={database_sec.secure_mode},"
            f" growth_factor={database_sec.growth_factor},"
            f" cats={cats_str},"
            f" dogs={dogs_str},"
            f" sasquatch=(),"
            f" big_foot={big_foot_str},"
            f" secret_files={secret_files_str},"
            f" more_files={more_files_str},"
            f" fibonacci={set(database_sec.fibonacci)},"
            f" more_fibonacci={database_sec.more_fibonacci},"
            f" holidays={holidays_str},"
            f" non_holidays={non_holidays_str},"
            f" old_tokens={old_tokens_str},"
            f" future_tokens={future_tokens_str},"
            f" needs_escaping='{needs_escaping_str}'"
            f")"
        )

        self.expected_database_repr = (
            f"DatabaseSection(\n"
            f"    user={repr(database_sec.user)},\n"
            f"    password=Unset,\n"
            f"    token={repr(database_sec.token)},\n"
            f"    birthday={repr(database_sec.birthday)},\n"
            f"    url={repr(database_sec.url)},\n"
            f"    port={repr(database_sec.port)},\n"
            f"    ultimate_question=None,\n"
            f"    no_collection=None,\n"
            f"    resources={repr(database_sec.resources)},\n"
            f"    rel_resources={repr(database_sec.rel_resources)},\n"
            f"    secure_mode={repr(database_sec.secure_mode)},\n"
            f"    growth_factor={repr(database_sec.growth_factor)},\n"
            f"    cats={repr(database_sec.cats)},\n"
            f"    dogs={repr(database_sec.dogs)},\n"
            f"    sasquatch={repr(database_sec.sasquatch)},\n"
            f"    big_foot={repr(database_sec.big_foot)},\n"
            f"    secret_files={repr(database_sec.secret_files)},\n"
            f"    more_files={repr(database_sec.more_files)},\n"
            f"    fibonacci={repr(database_sec.fibonacci)},\n"
            f"    more_fibonacci={repr(database_sec.more_fibonacci)},\n"
            f"    holidays={repr(database_sec.holidays)},\n"
            f"    non_holidays={repr(database_sec.non_holidays)},\n"
            f"    old_tokens={repr(database_sec.old_tokens)},\n"
            f"    future_tokens={repr(database_sec.future_tokens)},\n"
            f"    needs_escaping={repr(database_sec.needs_escaping)},\n"
            f")"
        )

    def test_pretty_section_str(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):
                sec = _get_testing_section_cls(tps)()
                self.assertEqual(self.expected_database_str, str(sec))

    def test_pretty_empty_section_str(self):
        sec = EmptySection()
        self.assertEqual("EmptySection()", str(sec))

    def test_pretty_section_repr(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):
                sec = _get_testing_section_cls(tps)()
                self.assertEqual(self.expected_database_repr, repr(sec))

    def test_pretty_empty_section_repr(self):
        sec = EmptySection()
        self.assertEqual("EmptySection(\n)", repr(sec))

    def test_pretty_config_str(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):
                cfg = _get_big_testing_config_cls(tps)()
                self.assertEqual(
                    f"BigConfig(database={cfg.database}, empty={cfg.empty})", str(cfg)
                )

    def test_pretty_empty_config_str(self):
        cfg = EmptyConfig()
        self.assertEqual("EmptyConfig()", str(cfg))

    def test_pretty_config_repr(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):
                cfg = _get_big_testing_config_cls(tps)()
                self.assertEqual(
                    (
                        f"BigConfig(\n"
                        f"    database={indent_after_newline(repr(cfg.database))},\n"
                        f"    empty={indent_after_newline(repr(cfg.empty))},\n"
                        f")"
                    ),
                    repr(cfg),
                )

    def test_pretty_empty_config_repr(self):
        cfg = EmptyConfig()
        self.assertEqual("EmptyConfig(\n)", repr(cfg))

    def test_config_str_and_repr_after_mutation(self):
        class MySection(ConfigSection):
            my_entry: int = 42

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()
        update_section(cfg.my_section, my_entry=7)

        self.assertEqual(f"MyConfig(my_section=MySection(my_entry=7))", str(cfg))
        self.assertEqual(
            (
                f"MyConfig(\n"
                f"    my_section=MySection(\n"
                f"        my_entry=7,\n"
                f"    ),\n"
                f")"
            ),
            repr(cfg),
        )

    def test_section_and_config_str_and_repr_with_secret(self):
        class MySection(ConfigSection):
            my_int: int = 42
            my_secret: SecretString
            my_none_secret: Optional[SecretString] = None

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()
        update_section(cfg.my_section, my_secret="hello, world!")

        self.assertEqual(
            f"MySection(my_int=42, my_secret='*****', my_none_secret=None)",
            str(cfg.my_section),
        )
        self.assertEqual(
            (
                f"MySection(\n"
                f"    my_int=42,\n"
                f"    my_secret={repr('*****')},\n"
                f"    my_none_secret=None,\n"
                f")"
            ),
            repr(cfg.my_section),
        )

        self.assertEqual(f"MyConfig(my_section={cfg.my_section})", str(cfg))
        self.assertEqual(
            (
                f"MyConfig(\n"
                f"    my_section={indent_after_newline(repr(cfg.my_section))},\n"
                f")"
            ),
            repr(cfg),
        )

    def test_secret_string_masking_in_collections(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    my_tuple: tps.tuple[SecretString, ...]
                    my_frozenset: Optional[tps.frozenset[SecretString]] = None
                    my_empty_tuple: tps.tuple[SecretString, ...] = ()
                    my_empty_frozenset: tps.frozenset[SecretString] = frozenset()
                    my_none: Optional[tps.tuple[SecretString, ...]] = None

                class MyConfig(Config):
                    my_section: MySection

                cfg = MyConfig()
                update_section(
                    cfg.my_section,
                    my_tuple=("hello",),
                    my_frozenset=frozenset(("goodbye", "see ya!")),
                )

                self.assertEqual(
                    (
                        "MySection(my_tuple=('*****', ...), my_frozenset={'*****', ...},"
                        " my_empty_tuple=(), my_empty_frozenset={}, my_none=None)"
                    ),
                    str(cfg.my_section),
                )

                my_tuple_str = repr((...,)).replace(
                    "Ellipsis,", f"{repr('*****')}, ..."
                )
                my_frozenset_str = repr(frozenset((...,))).replace(
                    "Ellipsis", f"{repr('*****')}, ..."
                )

                self.assertEqual(
                    (
                        f"MySection(\n"
                        f"    my_tuple={my_tuple_str},\n"
                        f"    my_frozenset={my_frozenset_str},\n"
                        f"    my_empty_tuple={repr(())},\n"
                        f"    my_empty_frozenset={repr(frozenset())},\n"
                        f"    my_none=None,\n"
                        f")"
                    ),
                    repr(cfg.my_section),
                )
