from sys import getsizeof
from unittest import TestCase

from nx_config import ConfigSection


class SectionTestCase(TestCase):
    def test_section_subclass_init_forbidden(self):
        with self.assertRaises(ValueError) as ctx:
            class MySection(ConfigSection):
                def __init__(self):
                    super(MySection, self).__init__()

        msg = str(ctx.exception)
        self.assertIn("'__init__'", msg)

    def test_empty_section_subclass_has_default_init(self):
        _ = self

        class MySection(ConfigSection):
            pass

        _ = MySection()

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
        self.assertEqual(str(sec.my_entry), "Unset")
        self.assertEqual(repr(sec.my_entry), "Unset")
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

        self.assertLess(getsizeof(MySection().my_entry), 20)

    def test_cannot_get_undeclared_entry(self):
        class MySection(ConfigSection):
            pass

        with self.assertRaises(AttributeError):
            # noinspection PyUnresolvedReferences
            _ = MySection().undeclared_entry

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
        class MySection(ConfigSection):
            pass

        sec = MySection()

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

        self.assertEqual(MySection().my_entry, 42)

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

    # TODO: Allow methods and nested type definitions (and aliases?). Add validator annotation.
    #   Default values must satisfy validators. Pretty printing (+SecretString).
