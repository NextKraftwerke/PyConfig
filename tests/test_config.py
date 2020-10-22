from unittest import TestCase

from nx_config import Config, ConfigSection


class EmptySection(ConfigSection):
    pass


class ConfigTestCase(TestCase):
    def test_config_subclass_init_forbidden(self):
        with self.assertRaises(ValueError):
            class MyConfig(Config):
                def __init__(self):
                    super(MyConfig, self).__init__()

    def test_empty_config_subclass_has_default_init(self):
        _ = self

        class MyConfig(Config):
            pass

        _ = MyConfig()

    def test_config_can_have_sections(self):
        _ = self

        # noinspection PyUnusedLocal
        class MyConfig(Config):
            my_section: EmptySection

    def test_section_cannot_be_protected(self):
        with self.assertRaises(ValueError):
            # noinspection PyUnusedLocal
            class MyConfig(Config):
                _my_section: EmptySection

    def test_sections_must_be_case_insensitively_unique(self):
        with self.assertRaises(ValueError):
            # noinspection PyUnusedLocal
            class MyConfig(Config):
                my_section: EmptySection
                My_SectioN: EmptySection
