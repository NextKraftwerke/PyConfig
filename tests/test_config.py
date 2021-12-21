from datetime import timedelta
from unittest import TestCase

from nx_config import Config, ConfigSection


class EmptySection(ConfigSection):
    pass


class ConfigTestCase(TestCase):
    def test_config_subclass_init_forbidden(self):
        with self.assertRaises(ValueError) as ctx:
            # noinspection PyUnusedLocal
            class MyConfig(Config):
                def __init__(self):
                    super().__init__()

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

    def test_special_default_section_is_forbidden(self):
        with self.assertRaises(ValueError) as ctx1:
            # noinspection PyUnusedLocal
            class MyConfig1(Config):
                default: EmptySection

        msg1 = str(ctx1.exception)
        self.assertIn("'default'", msg1)
        self.assertIn("case", msg1.lower())
        self.assertIn("ini", msg1.lower())
        self.assertIn("special", msg1.lower())

        with self.assertRaises(ValueError) as ctx2:
            # noinspection PyUnusedLocal
            class MyConfig2(Config):
                DEFAULT: EmptySection

        msg2 = str(ctx2.exception)
        self.assertIn("'default'", msg2)
        self.assertIn("case", msg2.lower())
        self.assertIn("ini", msg2.lower())
        self.assertIn("special", msg2.lower())

        with self.assertRaises(ValueError) as ctx3:
            # noinspection PyUnusedLocal
            class MyConfig3(Config):
                DeFaUlT: EmptySection

        msg3 = str(ctx3.exception)
        self.assertIn("'default'", msg3)
        self.assertIn("case", msg3.lower())
        self.assertIn("ini", msg3.lower())
        self.assertIn("special", msg3.lower())

    def test_sections_are_initially_immutable(self):
        class MySection(ConfigSection):
            my_entry: int
            my_entry_d: int = 42

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()
        self.assertIs(cfg.my_section.my_entry, MySection().my_entry)
        self.assertEqual(42, cfg.my_section.my_entry_d)

        with self.assertRaises(AttributeError) as ctx1:
            cfg.my_section.my_entry = 42

        msg1 = str(ctx1.exception)
        self.assertIn("set", msg1.lower())

        with self.assertRaises(AttributeError) as ctx2:
            cfg.my_section.my_entry_d = 42

        msg2 = str(ctx2.exception)
        self.assertIn("set", msg2.lower())

        self.assertIs(cfg.my_section.my_entry, MySection().my_entry)
        self.assertEqual(42, cfg.my_section.my_entry_d)

    def test_methods_are_okay(self):
        class MySection(ConfigSection):
            delta_in_minutes: int = 42

        class MyConfig(Config):
            my_section: MySection

            def delta(self) -> timedelta:
                return timedelta(minutes=self.my_section.delta_in_minutes)

        cfg = MyConfig()
        self.assertEqual(
            timedelta(minutes=cfg.my_section.delta_in_minutes), cfg.delta()
        )

    def test_nested_types_are_okay(self):
        class MySection(ConfigSection):
            temp_in_celsius: float = 36.5

        class MyConfig(Config):
            my_section: MySection

            class Temperature:
                def __init__(self, *, kelvin: float):
                    self.kelvin = kelvin

                def celsius(self) -> float:
                    return self.kelvin - 273.15

                @classmethod
                def from_celsius(cls, celsius: float):
                    return cls(kelvin=celsius + 273.15)

            def temp(self) -> Temperature:
                return MyConfig.Temperature.from_celsius(
                    self.my_section.temp_in_celsius
                )

        cfg = MyConfig()
        self.assertEqual(cfg.my_section.temp_in_celsius, cfg.temp().celsius())
