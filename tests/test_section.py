from sys import getsizeof
from unittest import TestCase

from nx_config import ConfigSection


class SectionTestCase(TestCase):
    def test_section_subclass_init_forbidden(self):
        with self.assertRaises(ValueError):
            class MySection(ConfigSection):
                def __init__(self):
                    super(MySection, self).__init__()

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
        with self.assertRaises(ValueError):
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                _my_entry: int

    def test_section_entries_must_be_case_insensitively_unique(self):
        with self.assertRaises(ValueError):
            # noinspection PyUnusedLocal
            class MySection(ConfigSection):
                my_entry: int
                My_Entry: float

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

    def test_cannot_set_entry(self):
        class MySection(ConfigSection):
            my_entry: int

        sec = MySection()

        with self.assertRaises(AttributeError):
            sec.my_entry = 42
