from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Any, Union
from unittest import TestCase, skipIf
from uuid import UUID

from nx_config import ConfigSection, SecretString, URL
from tests.typing_test_helpers import collection_type_holders


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
            my_datetime_d_tz: datetime = datetime(
                2020, 5, 4, tzinfo=timezone(timedelta(hours=2))
            )
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

        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    my_entry: tps.tuple[int, ...]
                    my_other_entry: tps.tuple[bool, ...] = some_bools

                sec = MySection()
                self.assertEqual(some_bools, sec.my_other_entry)

    def test_tuple_must_be_single_type_then_ellipsis(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):
                with self.assertRaises(TypeError) as ctx1:
                    # noinspection PyUnusedLocal
                    class MySection1(ConfigSection):
                        my_entry: tps.tuple[int, int]

                msg1 = str(ctx1.exception)
                self.assertIn("'my_entry'", msg1)
                self.assertIn(str(tps.tuple[int, int]), msg1)

                with self.assertRaises(TypeError) as ctx2:
                    # noinspection PyUnusedLocal
                    class MySection2(ConfigSection):
                        my_entry: tps.tuple[int]

                msg2 = str(ctx2.exception)
                self.assertIn("'my_entry'", msg2)
                self.assertIn(str(tps.tuple[int]), msg2)

    def test_nice_type_str_if_invalid_type(self):
        class Foo:
            pass

        with self.assertRaises(TypeError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry: Foo

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertNotIn(str(Foo), msg)

    def test_tuple_is_not_optional(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):
                with self.assertRaises(TypeError) as ctx:
                    # noinspection PyUnusedLocal
                    class MySection(ConfigSection):
                        my_entry: tps.tuple[int, ...] = None

                msg = str(ctx.exception)
                self.assertIn("'my_entry'", msg)
                self.assertIn("NoneType", msg)
                self.assertIn(str(tps.tuple[int, ...]), msg)
                self.assertIn("default value", msg.lower())

    def test_tuple_elements_must_have_base_type(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):
                with self.assertRaises(TypeError) as ctx:
                    # noinspection PyUnusedLocal
                    class MySection(ConfigSection):
                        my_entry: tps.tuple[int, ...] = (42, "43", 44, 45)

                msg = str(ctx.exception)
                self.assertIn("'my_entry'", msg)
                self.assertIn(str(tps.tuple[int, ...]), msg)
                self.assertIn("element", msg.lower())
                self.assertIn("default value", msg.lower())

    def test_tuple_must_be_tuple(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):
                with self.assertRaises(TypeError) as ctx1:
                    # noinspection PyUnusedLocal
                    class MySection1(ConfigSection):
                        my_entry: tps.tuple[int, ...] = frozenset((42, 43, 44, 45))

                msg1 = str(ctx1.exception)
                self.assertIn("'my_entry'", msg1)
                self.assertIn(str(tps.tuple[int, ...]), msg1)
                self.assertIn("frozenset", msg1)
                self.assertIn("default value", msg1.lower())

                with self.assertRaises(TypeError) as ctx2:
                    # noinspection PyUnusedLocal
                    class MySection2(ConfigSection):
                        my_entry: tps.tuple[int, ...] = 42.0

                msg2 = str(ctx2.exception)
                self.assertIn("'my_entry'", msg2)
                self.assertIn(str(tps.tuple[int, ...]), msg2)
                self.assertIn("float", msg2)
                self.assertIn("default value", msg2.lower())

    def test_tuple_can_be_empty(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    my_entry: tps.tuple[int, ...] = ()

                sec = MySection()
                self.assertEqual((), sec.my_entry)

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

    def test_union_without_none_is_not_supported(self):
        with self.assertRaises(TypeError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry: Union[int, str]

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("Union[int, str]", msg)

    def test_union_with_none_is_optional(self):
        class MySection(ConfigSection):
            none_as_first: Union[None, int] = None
            none_as_first42: Union[None, int] = 42
            none_as_second: Union[int, None] = None
            none_as_second42: Union[int, None] = 42

        sec = MySection()
        self.assertIsNone(sec.none_as_first)
        self.assertEqual(42, sec.none_as_first42)
        self.assertIsNone(sec.none_as_second)
        self.assertEqual(42, sec.none_as_second42)

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
        self.assertIn(str(Optional[int]), msg)
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
        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    my_entry: Optional[tps.tuple[SecretString, ...]]
                    my_second_entry: Optional[tps.tuple[SecretString, ...]] = None
                    my_third_entry: Optional[tps.frozenset[SecretString]] = None

                sec = MySection()
                self.assertIsNotNone(sec.my_entry)
                self.assertIsNone(sec.my_second_entry)
                self.assertIsNone(sec.my_third_entry)

    def test_collection_of_secret_strings_can_be_empty(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    my_entry: tps.tuple[SecretString, ...]
                    my_second_entry: tps.tuple[SecretString, ...] = ()
                    my_third_entry: tps.frozenset[SecretString] = frozenset()
                    my_fourth_entry: Optional[tps.tuple[SecretString, ...]] = ()
                    my_fifth_entry: Optional[tps.frozenset[SecretString]] = frozenset()

                sec = MySection()
                self.assertEqual("Unset", str(sec.my_entry))
                self.assertEqual((), sec.my_second_entry)
                self.assertEqual(frozenset(), sec.my_third_entry)
                self.assertEqual((), sec.my_fourth_entry)
                self.assertEqual(frozenset(), sec.my_fifth_entry)

    def test_tuple_can_be_optional(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    my_entry: Optional[tps.tuple[int, ...]] = None
                    my_other_entry: Optional[tps.tuple[int, ...]] = (42,)

                sec = MySection()
                self.assertIsNone(sec.my_entry)
                self.assertEqual((42,), sec.my_other_entry)

    def test_frozenset_is_ok(self):
        some_strings = frozenset(("hello", "hi", "howdy?!"))

        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    my_entry: tps.frozenset[int]
                    my_other_entry: tps.frozenset[str] = some_strings

                sec = MySection()
                self.assertEqual(some_strings, sec.my_other_entry)

    def test_no_lists_allowed(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):
                with self.assertRaises(TypeError) as ctx:
                    # noinspection PyUnusedLocal
                    class MySection(ConfigSection):
                        my_entry: tps.list[int]

                msg = str(ctx.exception)
                self.assertIn("'my_entry'", msg)
                self.assertIn("list", msg.lower())
                self.assertIn("tuple", msg.lower())

    def test_list_is_not_tuple(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):
                with self.assertRaises(TypeError) as ctx:
                    # noinspection PyUnusedLocal
                    class MySection(ConfigSection):
                        my_entry: tps.tuple[int, ...] = [1, 2, 3]

                msg = str(ctx.exception)
                self.assertIn("'my_entry'", msg)
                self.assertIn(str(tps.tuple[int, ...]), msg)
                self.assertIn("list", msg)
                self.assertIn("default value", msg.lower())

    def test_frozenset_is_not_optional(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):
                with self.assertRaises(TypeError) as ctx:
                    # noinspection PyUnusedLocal
                    class MySection(ConfigSection):
                        my_entry: tps.frozenset[int] = None

                msg = str(ctx.exception)
                self.assertIn("'my_entry'", msg)
                self.assertIn("NoneType", msg)
                self.assertIn(str(tps.frozenset[int]), msg)
                self.assertIn("default value", msg.lower())

    def test_frozenset_elements_must_have_base_type(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):
                with self.assertRaises(TypeError) as ctx:
                    # noinspection PyUnusedLocal
                    class MySection(ConfigSection):
                        my_entry: tps.frozenset[int] = frozenset((42, "43", 44, 45))

                msg = str(ctx.exception)
                self.assertIn("'my_entry'", msg)
                self.assertIn(str(tps.frozenset[int]), msg)
                self.assertIn("element", msg.lower())
                self.assertIn("default value", msg.lower())

    def test_frozenset_must_be_frozenset(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):
                with self.assertRaises(TypeError) as ctx1:
                    # noinspection PyUnusedLocal
                    class MySection1(ConfigSection):
                        my_entry: tps.frozenset[int] = (42, 43, 44, 45)

                msg1 = str(ctx1.exception)
                self.assertIn("'my_entry'", msg1)
                self.assertIn(str(tps.frozenset[int]), msg1)
                self.assertIn("tuple", msg1)
                self.assertIn("default value", msg1.lower())

                with self.assertRaises(TypeError) as ctx2:
                    # noinspection PyUnusedLocal
                    class MySection2(ConfigSection):
                        my_entry: tps.frozenset[int] = 42.0

                msg2 = str(ctx2.exception)
                self.assertIn("'my_entry'", msg2)
                self.assertIn(str(tps.frozenset[int]), msg2)
                self.assertIn("float", msg2)
                self.assertIn("default value", msg2.lower())

    def test_frozenset_can_be_empty(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    my_entry: tps.frozenset[int] = frozenset()

                sec = MySection()
                self.assertEqual(frozenset(), sec.my_entry)

    def test_no_sets_allowed(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):
                with self.assertRaises(TypeError) as ctx:
                    # noinspection PyUnusedLocal
                    class MySection(ConfigSection):
                        my_entry: tps.set[int] = {1, 2, 3}

                msg = str(ctx.exception)
                self.assertIn("'my_entry'", msg)
                self.assertIn("set", msg.lower())
                self.assertIn("frozenset", msg.lower())

    def test_set_is_not_frozenset(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):
                with self.assertRaises(TypeError) as ctx:
                    # noinspection PyUnusedLocal
                    class MySection(ConfigSection):
                        my_entry: tps.frozenset[int] = {1, 2, 3}

                msg = str(ctx.exception)
                self.assertIn("'my_entry'", msg)
                self.assertIn(str(tps.frozenset[int]), msg)
                self.assertIn("set", msg)
                self.assertIn("default value", msg.lower())

    def test_no_mappings_allowed(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):
                with self.assertRaises(TypeError) as ctx:
                    # noinspection PyUnusedLocal
                    class MySection(ConfigSection):
                        my_entry: tps.dict[str, int] = {"a": 1, "b": 2, "c": 3}

                msg = str(ctx.exception)
                self.assertIn("'my_entry'", msg)
                self.assertIn("dict", msg.lower())

    def test_no_collections_of_optionals(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):
                with self.assertRaises(TypeError) as ctx:
                    # noinspection PyUnusedLocal
                    class MySection(ConfigSection):
                        my_entry: tps.tuple[Optional[int], ...]

                msg = str(ctx.exception)
                self.assertIn("'my_entry'", msg)
                self.assertIn(str(Optional[int]), msg)
                self.assertIn("element", msg.lower())

    @skipIf(
        len(collection_type_holders) < 2, "Nothing to mix if there's only one style"
    )
    def test_mixing_typing_and_builtin(self):
        tuple0 = collection_type_holders[0].tuple
        tuple1 = collection_type_holders[1].tuple
        some_bools = (True, True, False, True, False, False)
        some_ints = (42, 43, 44, 46)

        class MySection(ConfigSection):
            my_first_entry: tuple0[float, ...]
            my_second_entry: tuple0[bool, ...] = some_bools
            my_third_entry: tuple1[str, ...]
            my_fourth_entry: tuple1[int, ...] = some_ints

        sec = MySection()
        self.assertEqual(some_bools, sec.my_second_entry)
        self.assertEqual(some_ints, sec.my_fourth_entry)

    def test_no_bare_tuples(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):
                with self.assertRaises(TypeError) as ctx:
                    # noinspection PyUnusedLocal
                    class MySection(ConfigSection):
                        my_entry: tps.tuple

                msg = str(ctx.exception)
                self.assertIn("tuple", msg.lower())
                self.assertIn("bare", msg)

    def test_no_bare_frozensets(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):
                with self.assertRaises(TypeError) as ctx:
                    # noinspection PyUnusedLocal
                    class MySection(ConfigSection):
                        my_entry: tps.frozenset

                msg = str(ctx.exception)
                self.assertIn("frozenset", msg.lower())
                self.assertIn("bare", msg)
