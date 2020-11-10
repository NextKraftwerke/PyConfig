from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, FrozenSet, Tuple
from unittest import TestCase
from uuid import UUID

from nx_config import ConfigSection, URL, SecretString, validate, Config
from nx_config.test_utils import mutable_config


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
    no_collection: Optional[Tuple[int, ...]] = None
    resources: Path = Path("/a/b/c/resources/")
    rel_resources: Path = Path("c/resources")
    secure_mode: bool = True
    growth_factor: float = 1.5
    cats: Optional[FrozenSet[str]] = frozenset(("grey", "brown", "black", "white"))
    dogs: Tuple[str, ...] = ("lazy", "happy", "sad")
    sasquatch: Tuple[str, ...] = ()
    big_foot: FrozenSet[str] = frozenset()
    secret_files: FrozenSet[Path] = frozenset((Path("hi.txt"), Path("/hello.md")))
    more_files: Tuple[Path, ...] = (Path("bye.exe"), Path("/see_ya.py"))
    fibonacci: FrozenSet[int] = frozenset((0, 1, 1, 2, 3, 5))
    more_fibonacci: Tuple[int, ...] = (8, 13, 21, 34)
    holidays: FrozenSet[datetime] = frozenset((datetime(1985, 11, 12),))
    non_holidays: Tuple[datetime, ...] = (datetime(1985, 11, 13),)
    old_tokens: FrozenSet[UUID] = frozenset((UUID(int=1), UUID(int=9_999_999_999_999)))
    future_tokens: Tuple[UUID, ...] = (UUID(int=2), UUID(int=7), UUID(int=17))
    needs_escaping: str = "Hello\nWorld\r!\tHowdy?"

    class Nested:
        pass

    Alias = Nested

    def a_method(self):
        pass

    @validate
    def a_validator(self):
        pass


class EmptySection(ConfigSection):
    pass


class BigConfig(Config):
    database: DatabaseSection
    empty: EmptySection


class EmptyConfig(Config):
    pass


def indent_after_newline(s: str) -> str:
    return s.replace("\n", "\n    ")


class PrettyPrintingTestCase(TestCase):
    def setUp(self) -> None:
        database_sec = DatabaseSection()

        cats_str = "{" + ", ".join(f"'{x}'" for x in database_sec.cats) + "}"
        dogs_str = "(" + ", ".join(f"'{x}'" for x in database_sec.dogs) + ")"
        big_foot_str = "{}"
        secret_files_str = "{" + ", ".join(f"'{x}'" for x in database_sec.secret_files) + "}"
        more_files_str = "(" + ", ".join(f"'{x}'" for x in database_sec.more_files) + ")"
        holidays_str = "{" + ", ".join(str(x) for x in database_sec.holidays) + "}"
        non_holidays_str = "(" + ", ".join(str(x) for x in database_sec.non_holidays) + ")"
        old_tokens_str = "{" + ", ".join(str(x) for x in database_sec.old_tokens) + "}"
        future_tokens_str = "(" + ", ".join(str(x) for x in database_sec.future_tokens) + ")"
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
        sec = DatabaseSection()
        self.assertEqual(str(sec), self.expected_database_str)

    def test_pretty_empty_section_str(self):
        sec = EmptySection()
        self.assertEqual(str(sec), "EmptySection()")

    def test_pretty_section_repr(self):
        sec = DatabaseSection()
        self.assertEqual(repr(sec), self.expected_database_repr)

    def test_pretty_empty_section_repr(self):
        sec = EmptySection()
        self.assertEqual(repr(sec), "EmptySection(\n)")

    def test_pretty_config_str(self):
        cfg = BigConfig()
        self.assertEqual(str(cfg), f"BigConfig(database={cfg.database}, empty={cfg.empty})")

    def test_pretty_empty_config_str(self):
        cfg = EmptyConfig()
        self.assertEqual(str(cfg), "EmptyConfig()")

    def test_pretty_config_repr(self):
        cfg = BigConfig()
        self.assertEqual(
            repr(cfg),
            (
                f"BigConfig(\n"
                f"    database={indent_after_newline(repr(cfg.database))},\n"
                f"    empty={indent_after_newline(repr(cfg.empty))},\n"
                f")"
            )
        )

    def test_pretty_empty_config_repr(self):
        cfg = EmptyConfig()
        self.assertEqual(repr(cfg), "EmptyConfig(\n)")

    def test_config_str_and_repr_after_mutation(self):
        class MySection(ConfigSection):
            my_entry: int = 42

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()

        with mutable_config(cfg):
            cfg.my_section.my_entry = 7

        self.assertEqual(str(cfg), f"MyConfig(my_section=MySection(my_entry=7))")
        self.assertEqual(
            repr(cfg),
            (
                f"MyConfig(\n"
                f"    my_section=MySection(\n"
                f"        my_entry=7,\n"
                f"    ),\n"
                f")"
            ),
        )

    # TODO: SecretString masking in section.
    # TODO: SecretString masking in config.
    # TODO: SecretString masking in tuple.
    # TODO: SecretString masking in frozenset.
