from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, FrozenSet, Tuple
from unittest import TestCase
from uuid import UUID

from nx_config import ConfigSection, URL, SecretString


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


class PrettyPrintingTestCase(TestCase):
    def test_pretty_section_str(self):
        sec = DatabaseSection()

        cats_str = "{" + ", ".join(f"'{x}'" for x in sec.cats) + "}"
        dogs_str = "(" + ", ".join(f"'{x}'" for x in sec.dogs) + ")"
        big_foot_str = "{}"
        secret_files_str = "{" + ", ".join(f"'{x}'" for x in sec.secret_files) + "}"
        more_files_str = "(" + ", ".join(f"'{x}'" for x in sec.more_files) + ")"
        holidays_str = "{" + ", ".join(str(x) for x in sec.holidays) + "}"
        non_holidays_str = "(" + ", ".join(str(x) for x in sec.non_holidays) + ")"
        old_tokens_str = "{" + ", ".join(str(x) for x in sec.old_tokens) + "}"
        future_tokens_str = "(" + ", ".join(str(x) for x in sec.future_tokens) + ")"

        self.assertEqual(
            str(sec),
            (
                f"DatabaseSection(user='{sec.user}',"
                f" password=Unset,"
                f" token={sec.token},"
                f" birthday={sec.birthday},"
                f" url='{sec.url}',"
                f" port={sec.port},"
                f" ultimate_question=None,"
                f" no_collection=None,"
                f" resources='{sec.resources}',"
                f" rel_resources='{sec.rel_resources}',"
                f" secure_mode={sec.secure_mode},"
                f" growth_factor={sec.growth_factor},"
                f" cats={cats_str},"
                f" dogs={dogs_str},"
                f" sasquatch=(),"
                f" big_foot={big_foot_str},"
                f" secret_files={secret_files_str},"
                f" more_files={more_files_str},"
                f" fibonacci={set(sec.fibonacci)},"
                f" more_fibonacci={sec.more_fibonacci},"
                f" holidays={holidays_str},"
                f" non_holidays={non_holidays_str},"
                f" old_tokens={old_tokens_str},"
                f" future_tokens={future_tokens_str}"
                f")"
            ),
        )

    def test_pretty_empty_section_str(self):
        class MySection(ConfigSection):
            pass

        sec = MySection()
        self.assertEqual(str(sec), "MySection()")

    def test_pretty_section_str_escape_char_in_value_gets_backslash(self):
        class MySection(ConfigSection):
            my_entry: str = "Hello\nWorld\r!\tHowdy?"

        sec = MySection()
        self.assertEqual(str(sec), "MySection(my_entry='Hello\\nWorld\\r!\\tHowdy?')")

    def test_pretty_section_repr(self):
        sec = DatabaseSection()

        self.assertEqual(
            repr(sec),
            (
                f"DatabaseSection(\n"
                f"    user={repr(sec.user)},\n"
                f"    password=Unset,\n"
                f"    token={repr(sec.token)},\n"
                f"    birthday={repr(sec.birthday)},\n"
                f"    url={repr(sec.url)},\n"
                f"    port={repr(sec.port)},\n"
                f"    ultimate_question=None,\n"
                f"    no_collection=None,\n"
                f"    resources={repr(sec.resources)},\n"
                f"    rel_resources={repr(sec.rel_resources)},\n"
                f"    secure_mode={repr(sec.secure_mode)},\n"
                f"    growth_factor={repr(sec.growth_factor)},\n"
                f"    cats={repr(sec.cats)},\n"
                f"    dogs={repr(sec.dogs)},\n"
                f"    sasquatch={repr(sec.sasquatch)},\n"
                f"    big_foot={repr(sec.big_foot)},\n"
                f"    secret_files={repr(sec.secret_files)},\n"
                f"    more_files={repr(sec.more_files)},\n"
                f"    fibonacci={repr(sec.fibonacci)},\n"
                f"    more_fibonacci={repr(sec.more_fibonacci)},\n"
                f"    holidays={repr(sec.holidays)},\n"
                f"    non_holidays={repr(sec.non_holidays)},\n"
                f"    old_tokens={repr(sec.old_tokens)},\n"
                f"    future_tokens={repr(sec.future_tokens)},\n"
                f")"
            ),
        )

    def test_pretty_empty_section_repr(self):
        class MySection(ConfigSection):
            pass

        sec = MySection()
        self.assertEqual(repr(sec), "MySection(\n)")

    def test_pretty_section_repr_escape_char_in_value_gets_backslash(self):
        class MySection(ConfigSection):
            my_entry: str = "Hello\nWorld\r!\tHowdy?"

        sec = MySection()
        self.assertEqual(repr(sec), "MySection(\n    my_entry='Hello\\nWorld\\r!\\tHowdy?',\n)")

    # TODO: Config str (single line).
    # TODO: Config repr (multiline).
    # TODO: SecretString masking in section.
    # TODO: SecretString masking in config.
    # TODO: SecretString masking in tuple.
    # TODO: SecretString masking in frozenset.
