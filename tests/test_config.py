from unittest import TestCase

from nx_config import Config, ConfigSection


class EmptySection(ConfigSection):
    pass


class ConfigTestCase(TestCase):
    def test_config_subclass_init_forbidden(self):
        with self.assertRaises(ValueError) as ctx:
            class MyConfig(Config):
                def __init__(self):
                    super(MyConfig, self).__init__()

        msg = str(ctx.exception)
        self.assertIn("'__init__'", msg)

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
        with self.assertRaises(ValueError) as ctx:
            # noinspection PyUnusedLocal
            class MyConfig(Config):
                _my_section: EmptySection

        msg = str(ctx.exception)
        self.assertIn("'_my_section'", msg)
        self.assertIn("underscore", msg.lower())

    def test_sections_must_be_case_insensitively_unique(self):
        with self.assertRaises(ValueError) as ctx:
            # noinspection PyUnusedLocal
            class MyConfig(Config):
                my_section: EmptySection
                My_SectioN: EmptySection

        msg = str(ctx.exception)
        self.assertIn("case-insensitive", msg.lower())

    def test_sections_are_not_class_attributes(self):
        class MyConfig(Config):
            my_section: EmptySection

        with self.assertRaises(AttributeError):
            _ = MyConfig.my_section

    def test_sections_cannot_have_assigned_value(self):
        with self.assertRaises(ValueError) as ctx:
            # noinspection PyUnusedLocal
            class MyConfig(Config):
                my_section: EmptySection = EmptySection()

        msg = str(ctx.exception)
        self.assertIn("'my_section'", msg)

    def test_cannot_have_attributes_with_assigned_values(self):
        with self.assertRaises(ValueError) as ctx1:
            # noinspection PyUnusedLocal
            class MyConfig1(Config):
                my_int = 42

        msg1 = str(ctx1.exception)
        self.assertIn("'my_int'", msg1)

        with self.assertRaises(ValueError) as ctx2:
            # noinspection PyUnusedLocal
            class MyConfig2(Config):
                my_int: int = 42

        msg2 = str(ctx2.exception)
        self.assertIn("'my_int'", msg2)
