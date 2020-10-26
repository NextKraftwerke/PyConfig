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

    def test_config_subclass_cannot_define_slots(self):
        with self.assertRaises(ValueError) as ctx:
            # noinspection PyUnusedLocal
            class MyConfig(Config):
                __slots__ = ("something",)

        msg = str(ctx.exception)
        self.assertIn("'__slots__'", msg)

    def test_config_subclass_does_not_use_dict(self):
        class MyConfig(Config):
            my_section: EmptySection

        cfg = MyConfig()

        with self.assertRaises(AttributeError):
            _ = cfg.__dict__

    def test_config_subclass_can_have_docstring(self):
        _ = self

        class MyConfig(Config):
            """This is MyConfig's docstring."""
            pass

        _ = MyConfig()

    def test_empty_config_subclass_has_default_init(self):
        _ = self

        class MyConfig(Config):
            pass

        _ = MyConfig()

    def test_config_can_have_sections(self):
        class MyConfig(Config):
            my_section: EmptySection

        cfg = MyConfig()
        self.assertIsInstance(cfg.my_section, EmptySection)

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

    def test_sections_cannot_have_assigned_value(self):
        with self.assertRaises(ValueError) as ctx1:
            # noinspection PyUnusedLocal
            class MyConfig1(Config):
                my_section: EmptySection = EmptySection()

        msg1 = str(ctx1.exception)
        self.assertIn("'my_section'", msg1)

        with self.assertRaises(ValueError) as ctx2:
            # noinspection PyUnusedLocal
            class MyConfig2(Config):
                my_section: EmptySection = 42

        msg2 = str(ctx2.exception)
        self.assertIn("'my_section'", msg2)

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

    def test_annotations_must_be_sections(self):
        class NotASection:
            pass

        with self.assertRaises(ValueError) as ctx:
            # noinspection PyUnusedLocal
            class MyConfig(Config):
                my_section: NotASection

        msg = str(ctx.exception)
        self.assertIn("'ConfigSection'", msg)
        self.assertIn("subclass", msg.lower())
        self.assertIn("'my_section'", msg)

    def test_cannot_get_undeclared_attr(self):
        class MyConfig(Config):
            pass

        with self.assertRaises(AttributeError):
            # noinspection PyUnresolvedReferences
            _ = MyConfig().undeclared_attr

    def test_cannot_set_undeclared_attr(self):
        class MyConfig(Config):
            pass

        cfg = MyConfig()

        with self.assertRaises(AttributeError):
            cfg.undeclared_attr = 42

    def test_cannot_set_section(self):
        class MyConfig(Config):
            my_section: EmptySection

        cfg1 = MyConfig()

        with self.assertRaises(AttributeError) as ctx1:
            cfg1.my_section = 42

        msg1 = str(ctx1.exception)
        self.assertIn("set", msg1.lower())

        cfg2 = MyConfig()

        with self.assertRaises(AttributeError) as ctx2:
            cfg2.my_section = EmptySection()

        msg2 = str(ctx2.exception)
        self.assertIn("set", msg2.lower())
