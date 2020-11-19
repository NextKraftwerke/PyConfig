from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Tuple, Any, Union, List, FrozenSet, Set, Dict
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

    def test_int_default_value_must_be_int(self):
        with self.assertRaises(TypeError) as ctx1:
            # noinspection PyUnusedLocal
            class MySection1(ConfigSection):
                my_entry: int = 42.0

        msg1 = str(ctx1.exception)
        self.assertIn("'my_entry'", msg1)
        self.assertIn("int", msg1)
        self.assertIn("float", msg1)
        self.assertIn("default value", msg1.lower())

        with self.assertRaises(TypeError) as ctx2:
            # noinspection PyUnusedLocal
            class MySection2(ConfigSection):
                my_entry: int = "42"

        msg2 = str(ctx2.exception)
        self.assertIn("'my_entry'", msg2)
        self.assertIn("int", msg2)
        self.assertIn("str", msg2)
        self.assertIn("default value", msg2.lower())

    def test_optional_int_default_can_be_unset(self):
        class MySection(ConfigSection):
            my_entry: Optional[int]

        sec = MySection()
        self.assertIsNotNone(sec.my_entry)

    def test_optional_int_default_can_be_none(self):
        class MySection(ConfigSection):
            my_entry: Optional[int] = None

        sec = MySection()
        self.assertIsNone(sec.my_entry)

    def test_int_is_not_optional(self):
        with self.assertRaises(TypeError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry: int = None

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("int", msg)
        self.assertIn("NoneType", msg)
        self.assertIn("default value", msg.lower())

    def test_tuple_is_ok(self):
        some_bools = (True, True, False, True, False, False)

        class MySection(ConfigSection):
            my_entry: Tuple[int, ...]
            my_other_entry: Tuple[bool, ...] = some_bools

        sec = MySection()
        self.assertEqual(sec.my_other_entry, some_bools)

    def test_tuple_must_be_single_type_then_ellipsis(self):
        with self.assertRaises(TypeError) as ctx1:
            # noinspection PyUnusedLocal
            class MySection1(ConfigSection):
                my_entry: Tuple[int, int]

        msg1 = str(ctx1.exception)
        self.assertIn("'my_entry'", msg1)
        self.assertIn("Tuple[int, int]", msg1)

        with self.assertRaises(TypeError) as ctx2:
            # noinspection PyUnusedLocal
            class MySection2(ConfigSection):
                my_entry: Tuple[int]

        msg2 = str(ctx2.exception)
        self.assertIn("'my_entry'", msg2)
        self.assertIn("Tuple[int]", msg2)

    def test_tuple_is_not_optional(self):
        with self.assertRaises(TypeError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry: Tuple[int, ...] = None

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("NoneType", msg)
        self.assertIn("Tuple[int, ...]", msg)
        self.assertIn("default value", msg.lower())

    def test_tuple_elements_must_have_base_type(self):
        with self.assertRaises(TypeError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry: Tuple[int, ...] = (42, "43", 44, 45)

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("Tuple[int, ...]", msg)
        self.assertIn("element", msg.lower())
        self.assertIn("default value", msg.lower())

    def test_tuple_must_be_tuple(self):
        with self.assertRaises(TypeError) as ctx1:
            # noinspection PyUnusedLocal
            class MySection1(ConfigSection):
                my_entry: Tuple[int, ...] = frozenset((42, 43, 44, 45))

        msg1 = str(ctx1.exception)
        self.assertIn("'my_entry'", msg1)
        self.assertIn("Tuple[int, ...]", msg1)
        self.assertIn("frozenset", msg1)
        self.assertIn("default value", msg1.lower())

        with self.assertRaises(TypeError) as ctx2:
            # noinspection PyUnusedLocal
            class MySection2(ConfigSection):
                my_entry: Tuple[int, ...] = 42.0

        msg2 = str(ctx2.exception)
        self.assertIn("'my_entry'", msg2)
        self.assertIn("Tuple[int, ...]", msg2)
        self.assertIn("float", msg2)
        self.assertIn("default value", msg2.lower())

    def test_tuple_can_be_empty(self):
        class MySection(ConfigSection):
            my_entry: Tuple[int, ...] = ()

        sec = MySection()
        self.assertEqual(sec.my_entry, ())

    def test_any_is_not_supported(self):
        with self.assertRaises(TypeError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry: Any

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("Any", msg)

    def test_big_union_is_not_supported(self):
        with self.assertRaises(TypeError) as ctx1:
            # noinspection PyUnusedLocal
            class MySection1(ConfigSection):
                my_entry: Union[int, None, str]

        msg1 = str(ctx1.exception)
        self.assertIn("'my_entry'", msg1)
        self.assertIn("Union[int, NoneType, str]", msg1)

        with self.assertRaises(TypeError) as ctx2:
            # noinspection PyUnusedLocal
            class MySection2(ConfigSection):
                my_entry: Union[int, str, None]

        msg2 = str(ctx2.exception)
        self.assertIn("'my_entry'", msg2)
        self.assertIn("Union[int, str, NoneType]", msg2)

    def test_union_without_none_as_second_is_not_supported(self):
        with self.assertRaises(TypeError) as ctx1:
            # noinspection PyUnusedLocal
            class MySection1(ConfigSection):
                my_entry: Union[int, str]

        msg1 = str(ctx1.exception)
        self.assertIn("'my_entry'", msg1)
        self.assertIn("Union[int, str]", msg1)

        with self.assertRaises(TypeError) as ctx2:
            # noinspection PyUnusedLocal
            class MySection2(ConfigSection):
                my_entry: Union[None, str]

        msg2 = str(ctx2.exception)
        self.assertIn("'my_entry'", msg2)
        self.assertIn("Union[NoneType, str]", msg2)

    def test_optional_int_entry_can_be_none(self):
        class MySection(ConfigSection):
            my_entry: Optional[int] = None

        sec = MySection()
        self.assertIsNone(sec.my_entry)

    def test_optional_int_entry_cannot_be_str(self):
        with self.assertRaises(TypeError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry: Optional[int] = "hello"

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("str", msg)
        self.assertIn("Union[int, NoneType]", msg)
        self.assertIn("default value", msg.lower())

    def test_optional_secret_string_can_be_none(self):
        class MySection(ConfigSection):
            my_entry: Optional[SecretString]
            my_other_entry: Optional[SecretString] = None

        sec = MySection()
        self.assertIsNotNone(sec.my_entry)
        self.assertIsNone(sec.my_other_entry)

    def test_optional_secret_string_cannot_be_int(self):
        with self.assertRaises(TypeError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry: Optional[SecretString] = 42

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("SecretString", msg)
        self.assertIn("default value", msg.lower())

    def test_optional_secret_string_cannot_be_str(self):
        with self.assertRaises(ValueError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry: Optional[SecretString] = "hello"

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("SecretString", msg)
        self.assertIn("default value", msg.lower())

    def test_optional_collection_of_secret_strings_can_be_none(self):
        class MySection(ConfigSection):
            my_entry: Optional[Tuple[SecretString, ...]]
            my_second_entry: Optional[Tuple[SecretString, ...]] = None
            my_third_entry: Optional[FrozenSet[SecretString]] = None

        sec = MySection()
        self.assertIsNotNone(sec.my_entry)
        self.assertIsNone(sec.my_second_entry)
        self.assertIsNone(sec.my_third_entry)

    def test_collection_of_secret_strings_can_be_empty(self):
        class MySection(ConfigSection):
            my_entry: Tuple[SecretString, ...]
            my_second_entry: Tuple[SecretString, ...] = ()
            my_third_entry: FrozenSet[SecretString] = frozenset()
            my_fourth_entry: Optional[Tuple[SecretString, ...]] = ()
            my_fifth_entry: Optional[FrozenSet[SecretString]] = frozenset()

        sec = MySection()
        self.assertEqual(str(sec.my_entry), "Unset")
        self.assertEqual(sec.my_second_entry, ())
        self.assertEqual(sec.my_third_entry, frozenset())
        self.assertEqual(sec.my_fourth_entry, ())
        self.assertEqual(sec.my_fifth_entry, frozenset())

    def test_tuple_can_be_optional(self):
        class MySection(ConfigSection):
            my_entry: Optional[Tuple[int, ...]] = None
            my_other_entry: Optional[Tuple[int, ...]] = (42,)

        sec = MySection()
        self.assertIsNone(sec.my_entry)
        self.assertEqual(sec.my_other_entry, (42,))

    def test_frozenset_is_ok(self):
        some_strings = frozenset(("hello", "hi", "howdy?!"))

        class MySection(ConfigSection):
            my_entry: FrozenSet[int]
            my_other_entry: FrozenSet[str] = some_strings

        sec = MySection()
        self.assertEqual(sec.my_other_entry, some_strings)

    def test_no_lists_allowed(self):
        with self.assertRaises(TypeError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry: List[int]

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("list", msg.lower())
        self.assertIn("tuple", msg.lower())

    def test_list_is_not_tuple(self):
        with self.assertRaises(TypeError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry: Tuple[int, ...] = [1, 2, 3]

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("Tuple[int, ...]", msg)
        self.assertIn("list", msg)
        self.assertIn("default value", msg.lower())

    def test_frozenset_is_not_optional(self):
        with self.assertRaises(TypeError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry: FrozenSet[int] = None

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("NoneType", msg)
        self.assertIn("FrozenSet[int]", msg)
        self.assertIn("default value", msg.lower())

    def test_frozenset_elements_must_have_base_type(self):
        with self.assertRaises(TypeError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry: FrozenSet[int] = frozenset((42, "43", 44, 45))

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("FrozenSet[int]", msg)
        self.assertIn("element", msg.lower())
        self.assertIn("default value", msg.lower())

    def test_frozenset_must_be_frozenset(self):
        with self.assertRaises(TypeError) as ctx1:
            # noinspection PyUnusedLocal
            class MySection1(ConfigSection):
                my_entry: FrozenSet[int] = (42, 43, 44, 45)

        msg1 = str(ctx1.exception)
        self.assertIn("'my_entry'", msg1)
        self.assertIn("FrozenSet[int]", msg1)
        self.assertIn("tuple", msg1)
        self.assertIn("default value", msg1.lower())

        with self.assertRaises(TypeError) as ctx2:
            # noinspection PyUnusedLocal
            class MySection2(ConfigSection):
                my_entry: FrozenSet[int] = 42.0

        msg2 = str(ctx2.exception)
        self.assertIn("'my_entry'", msg2)
        self.assertIn("FrozenSet[int]", msg2)
        self.assertIn("float", msg2)
        self.assertIn("default value", msg2.lower())

    def test_frozenset_can_be_empty(self):
        class MySection(ConfigSection):
            my_entry: FrozenSet[int] = frozenset()

        sec = MySection()
        self.assertEqual(sec.my_entry, frozenset())

    def test_no_sets_allowed(self):
        with self.assertRaises(TypeError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry: Set[int] = {1, 2, 3}

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("set", msg.lower())
        self.assertIn("frozenset", msg.lower())

    def test_set_is_not_frozenset(self):
        with self.assertRaises(TypeError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry: FrozenSet[int] = {1, 2, 3}

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("FrozenSet[int]", msg)
        self.assertIn("set", msg)
        self.assertIn("default value", msg.lower())

    def test_no_mappings_allowed(self):
        with self.assertRaises(TypeError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry: Dict[str, int] = {"a": 1, "b": 2, "c": 3}

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("dict", msg.lower())

    def test_no_collections_of_optionals(self):
        with self.assertRaises(TypeError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry: Tuple[Optional[int], ...]

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("Union[int, NoneType]", msg)
        self.assertIn("element", msg.lower())
