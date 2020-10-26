from unittest import TestCase

from nx_config import Config, ConfigSection
from nx_config.test_utils import mutable_config


class EmptySection(ConfigSection):
    pass


class MutableConfigTestCase(TestCase):
    def test_can_use_test_util_on_empty_config(self):
        _ = self

        class MyConfig(Config):
            pass

        cfg = MyConfig()

        with mutable_config(cfg):
            pass

    def test_can_set_entries_with_test_util(self):
        class MySection(ConfigSection):
            my_entry: int
            my_entry_d: int = 42

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()
        self.assertIs(cfg.my_section.my_entry, MySection().my_entry)
        self.assertEqual(cfg.my_section.my_entry_d, 42)

        with mutable_config(cfg):
            cfg.my_section.my_entry = 7
            cfg.my_section.my_entry_d = 99

        self.assertEqual(cfg.my_section.my_entry, 7)
        self.assertEqual(cfg.my_section.my_entry_d, 99)

    def test_sections_are_immutable_after_test_util(self):
        class MySection(ConfigSection):
            my_entry: int = 42

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()

        with mutable_config(cfg):
            cfg.my_section.my_entry = 7

        with self.assertRaises(AttributeError):
            cfg.my_section.my_entry = 123

    def test_sections_are_immutable_after_exception_in_test_util(self):
        class MySection(ConfigSection):
            my_entry: int = 42

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()

        try:
            with mutable_config(cfg):
                raise ValueError()
        except ValueError:
            pass

        with self.assertRaises(AttributeError):
            cfg.my_section.my_entry = 123

    def test_cannot_set_sections_with_test_util(self):
        class MyConfig(Config):
            my_section: EmptySection

        cfg = MyConfig()

        with self.assertRaises(AttributeError):
            with mutable_config(cfg):
                cfg.my_section = EmptySection()

    def test_cannot_set_new_attr_with_test_util(self):
        class MyConfig(Config):
            pass

        cfg = MyConfig()

        with self.assertRaises(AttributeError):
            with mutable_config(cfg):
                cfg.my_int = 42

    def test_cannot_set_new_entries_with_test_util(self):
        class MyConfig(Config):
            my_section: EmptySection

        cfg = MyConfig()

        with self.assertRaises(AttributeError):
            with mutable_config(cfg):
                cfg.my_section.my_int = 42

    def test_test_util_is_instance_specific(self):
        class MySection(ConfigSection):
            my_entry: int = 42

        class MyConfig(Config):
            my_section: MySection

        cfg1 = MyConfig()
        cfg2 = MyConfig()

        with self.assertRaises(AttributeError):
            with mutable_config(cfg1):
                cfg2.my_section.my_entry = 9

    def test_can_have_different_config_instances(self):
        class MySection(ConfigSection):
            my_entry: int = 42

        class MyConfig(Config):
            my_section: MySection

        cfg1 = MyConfig()
        cfg2 = MyConfig()

        with mutable_config(cfg1):
            cfg1.my_section.my_entry = 9

        self.assertNotEqual(cfg1.my_section.my_entry, cfg2.my_section.my_entry)

    # TODO: Assigned values must satisfy validators.