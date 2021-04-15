from unittest import TestCase

from nx_config import fill_config, Config, ConfigSection, validate, ValidationError, IncompleteSectionError


class FillConfigNoInputTestCase(TestCase):
    def test_fill_no_input_empty_config(self):
        _ = self

        class MyConfig(Config):
            pass

        cfg = MyConfig()
        fill_config(cfg)

    def test_fill_no_input_empty_section(self):
        _ = self

        class MySection(ConfigSection):
            pass

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()
        fill_config(cfg)

    def test_fill_no_input(self):
        class MySection(ConfigSection):
            my_int: int = 42
            my_str: str = "Hello"

            @validate
            def str_not_too_long(self):
                if len(self.my_str) > self.my_int:
                    raise ValueError()

        class MySecondSection(ConfigSection):
            my_bool: bool = True

        class MyConfig(Config):
            first: MySection
            second: MySecondSection

        cfg = MyConfig()
        fill_config(cfg)

        with self.subTest("no_changes"):
            self.assertEqual(42, cfg.first.my_int)
            self.assertEqual("Hello", cfg.first.my_str)
            self.assertEqual(True, cfg.second.my_bool)

        with self.subTest("remains_immutable"):
            with self.assertRaises(AttributeError):
                cfg.first.my_int = 7

    def test_fill_no_input_missing_entry(self):
        class MySection(ConfigSection):
            my_bool: bool = False
            my_int: int
            my_str: str = "Hello"

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()

        with self.assertRaises(IncompleteSectionError) as ctx:
            fill_config(cfg)

        msg = str(ctx.exception)
        self.assertIn("'my_int'", msg)
        self.assertIn("'my_section'", msg)
        self.assertIn("set", msg.lower())
        self.assertIn("default value", msg.lower())

    def test_fill_no_input_failing_validator(self):
        expected_in_msg = "la la doo-di-loo-dah"

        class MySection(ConfigSection):
            @validate
            def just_pass(self):
                pass

            @validate
            def just_fail(self):
                raise ValueError(expected_in_msg)

            @validate
            def just_pass_again(self):
                pass

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()

        with self.assertRaises(ValidationError) as ctx:
            fill_config(cfg)

        msg = str(ctx.exception)
        self.assertIn(expected_in_msg, msg)
