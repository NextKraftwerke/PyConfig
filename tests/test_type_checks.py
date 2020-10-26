from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import TestCase
from uuid import UUID

from nx_config import ConfigSection, SecretString, URL


class TypeChecksTestCase(TestCase):
    def test_allowed_entry_non_collection_non_optional_type_hints(self):
        _ = self

        # noinspection PyUnusedLocal
        class MySection(ConfigSection):
            my_int: int
            my_int_d: int = 42
            my_float: float
            my_float_d: float = 3.14
            my_bool: bool
            my_bool_d: bool = False
            my_str: str
            my_str_d: str = "Hello"
            my_uuid: UUID
            my_uuid_d: UUID = UUID(int=1_234_567_890)
            my_datetime: datetime
            my_datetime_d_naive: datetime = datetime(2020, 5, 4)
            my_datetime_d_tz: datetime = datetime(2020, 5, 4, tzinfo=timezone(timedelta(hours=2)))
            my_path: Path
            my_path_d_abs: Path = Path("/a/b/c.txt")
            my_path_d_rel: Path = Path("a/b/c.txt")
            my_secret_string: SecretString
            # No default values for SecretString...
            my_url: URL
            my_url_d_http: URL = "http://www.abcdefg.com"
            my_url_d_https: URL = "https://www.abcdefg.com"
            my_url_d_ip: URL = "http://127.0.0.1:1234"
            my_url_d_local: URL = "http://localhost:1234"

    def test_secret_string_cannot_have_default_value(self):
        with self.assertRaises(ValueError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry: SecretString = "abcde12345"

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("'SecretString'", msg)
        self.assertIn("default value", msg.lower())

    # TODO: Test forbidden types, optional base types, collection types, optional collection types,
    #   default values must satisfy types, assigned values must satisfy types.
