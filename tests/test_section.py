from datetime import timedelta
from sys import getsizeof
from typing import Optional
from unittest import TestCase

from nx_config import ConfigSection, validate


class EmptySection(ConfigSection):
    pass


class SectionTestCase(TestCase):
    def test_section_subclass_init_forbidden(self):
        with self.assertRaises(ValueError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                def __init__(self):
                    super().__init__()

        msg = str(ctx.exception)
        self.assertIn("'__init__'", msg)

    def test_empty_section_subclass_has_default_init(self):
        _ = self
        _ = EmptySection()

    def test_section_can_have_entries(self):
        _ = self

        # noinspection PyUnusedLocal
        class MySection(ConfigSection):
            my_entry: int

    def test_section_entry_cannot_be_protected(self):
        with self.assertRaises(ValueError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                _my_entry: int

        msg = str(ctx.exception)
        self.assertIn("'_my_entry'", msg)
        self.assertIn("underscore", msg.lower())

    def test_section_entries_must_be_case_insensitively_unique(self):
        with self.assertRaises(ValueError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry: int
                My_Entry: float

        msg = str(ctx.exception)
        self.assertIn("case-insensitive", msg.lower())

    def test_entry_without_default_is_unset(self):
        class MySection(ConfigSection):
            my_entry: int

        sec = MySection()
        self.assertEqual("Unset", str(sec.my_entry))
        self.assertEqual("Unset", repr(sec.my_entry))
        self.assertIn("Unset", type(sec.my_entry).__name__)

    def test_unset_type_cannot_be_instantiated(self):
        class MySection(ConfigSection):
            my_entry: int

        unset_type = type(MySection().my_entry)

        with self.assertRaises(Exception):
            _ = unset_type()

        with self.assertRaises(Exception):
            _ = unset_type.__new__(unset_type)

    def test_unset_type_is_tiny(self):
        class MySection(ConfigSection):
            my_entry: int

        class Foo:
            pass

        self.assertLess(getsizeof(MySection().my_entry), getsizeof(Foo()))

    def test_cannot_get_undeclared_entry(self):
        with self.assertRaises(AttributeError):
            # noinspection PyUnresolvedReferences
            _ = EmptySection().undeclared_entry

    def test_cannot_set_entry(self):
        class MySection(ConfigSection):
            my_entry: int

        sec = MySection()

        with self.assertRaises(AttributeError) as ctx:
            sec.my_entry = 42

        self.assertIs(sec.my_entry, MySection().my_entry)

        msg = str(ctx.exception)
        self.assertIn("set", msg.lower())

    def test_cannot_set_undeclared_entry(self):
        sec = EmptySection()

        with self.assertRaises(AttributeError):
            sec.undeclared_entry = 42

    def test_cannot_declare_slots(self):
        with self.assertRaises(ValueError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                __slots__ = ("some_attribute",)

        msg = str(ctx.exception)
        self.assertIn("'__slots__'", msg)

    def test_section_subclass_does_not_use_dict(self):
        class MySection(ConfigSection):
            my_entry: int = 42
            my_other_entry: float

        sec = MySection()

        with self.assertRaises(AttributeError):
            _ = sec.__dict__

    def test_cannot_have_class_attr_without_type_hint(self):
        with self.assertRaises(ValueError) as ctx:
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry = 42

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)

    def test_entry_can_have_default_value(self):
        class MySection(ConfigSection):
            my_entry: int = 42

        self.assertEqual(42, MySection().my_entry)

    def test_section_can_have_docstring(self):
        _ = self

        # noinspection PyUnusedLocal
        class MySection(ConfigSection):
            """This is MySection's docstring."""

            pass

    def test_entry_mutable_name_collision(self):
        class MySection(ConfigSection):
            mutable: bool = True
            my_int: int = 0

        sec = MySection()

        with self.assertRaises(AttributeError):
            sec.my_int = 0

    def test_methods_are_okay(self):
        class MySection(ConfigSection):
            delta_in_minutes: int = 42

            def delta(self) -> timedelta:
                return timedelta(minutes=self.delta_in_minutes)

        sec = MySection()
        self.assertEqual(timedelta(minutes=sec.delta_in_minutes), sec.delta())

    def test_nested_types_are_okay(self):
        class MySection(ConfigSection):
            temp_in_celsius: float = 36.5

            class Temperature:
                def __init__(self, *, kelvin: float):
                    self.kelvin = kelvin

                def celsius(self) -> float:
                    return self.kelvin - 273.15

                @classmethod
                def from_celsius(cls, celsius: float):
                    return cls(kelvin=celsius + 273.15)

            def temp(self) -> Temperature:
                return MySection.Temperature.from_celsius(self.temp_in_celsius)

        sec = MySection()
        self.assertEqual(sec.temp_in_celsius, sec.temp().celsius())

    def test_can_have_validation_annotations(self):
        _ = self

        # noinspection PyUnusedLocal
        class MySection(ConfigSection):
            my_entry: int

            @validate
            def nop1(self):
                pass

            @validate
            def nop2(self):
                pass

    def test_no_validation_on_init(self):
        _ = self

        class MySection(ConfigSection):
            my_entry: int = 42

            @validate
            def will_never_pass(self):
                raise ValueError()

        _ = MySection()

    def test_double_star_unpack_empty_section(self):
        sec = EmptySection()
        self.assertDictEqual({}, {**sec})

    def test_double_star_unpack_non_empty_section(self):
        class MySection(ConfigSection):
            class ANestedClass:
                pass

            first: int = 42

            @validate
            def a_validator(self):
                pass

            second: float = 3.14
            third: bool = False

            class AnotherNestedClass:
                pass

            fourth: Optional[str] = None

            def a_method(self):
                pass

            fifth: Optional[str] = "Hello"

        sec = MySection()

        self.assertDictEqual(
            {
                "first": sec.first,
                "second": sec.second,
                "third": sec.third,
                "fourth": sec.fourth,
                "fifth": sec.fifth,
            },
            {**sec},
        )

    def test_empty_section_length(self):
        self.assertEqual(0, len(EmptySection()))

    def test_non_empty_section_length(self):
        class MySection(ConfigSection):
            first: int = 42
            second: float = 3.14
            third: bool = False
            fourth: Optional[str] = None
            fifth: Optional[str] = "Hello"

        self.assertEqual(5, len(MySection()))
