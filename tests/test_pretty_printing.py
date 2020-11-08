from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, FrozenSet, Tuple
from unittest import TestCase
from uuid import UUID

from nx_config import ConfigSection, URL, SecretString


class PrettyPrintingTestCase(TestCase):
    def test_pretty_section_str(self):
        tz = timezone(offset=timedelta(hours=-3))

        class DatabaseSection(ConfigSection):
            user: str = "John Doe"
            password: SecretString
            token: UUID = UUID(int=5_444_333_222_111)
            birthday: datetime = datetime(1955, 11, 5, 1, 22, tzinfo=tz)
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

        sec = DatabaseSection()

        cats_str = "{" + ", ".join(f"'{x}'" for x in sec.cats) + "}"
        dogs_str = "(" + ", ".join(f"'{x}'" for x in sec.dogs) + ")"
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
                f" sasquatch=())"
            ),
        )

    # TODO: Newlines in string values should become '\n' and not actual newlines.
    # TODO: repr should be multiline.
    # TODO: Config str (single line).
    # TODO: Config repr (multiline).
    # TODO: SecretString masking in section.
    # TODO: SecretString masking in config.
