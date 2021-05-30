from argparse import ArgumentParser
from io import StringIO
from unittest import TestCase

from nx_config import add_cli_options, Config, ConfigSection


class MyConfig(Config):
    class First(ConfigSection):
        entry_a: int
        entry_b: float = 0.1

    class Second(ConfigSection):
        entry_c: bool = True
        entry_d: str = ""

    first_sec: First
    second_sec: Second


class AddCLIOptionsTestCase(TestCase):
    def test_config_t_is_keyword_only(self):
        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            add_cli_options(ArgumentParser(), MyConfig)

    def test_no_prefix(self):
        prog = "my_program"
        parser = ArgumentParser(prog=prog)
        parser.add_argument("--foo")
        add_cli_options(parser, config_t=MyConfig)
        parser.add_argument("--bar")

        with self.subTest("With path arg"):
            expected_path = "/a/b/c.txt"
            args = parser.parse_args(("--foo", "f00", "--config-path", expected_path, "--bar=6aR"))
            self.assertEqual("f00", args.foo)
            self.assertEqual(expected_path, args.config_path)
            self.assertEqual("6aR", args.bar)

        with self.subTest("Without path arg"):
            args = parser.parse_args(("--foo", "f00", "--bar=6aR"))
            self.assertEqual("f00", args.foo)
            self.assertIsNone(args.config_path)
            self.assertEqual("6aR", args.bar)

        with self.subTest("Help"):
            ostream = StringIO()
            parser.print_help(ostream)
            msg = ostream.getvalue()
            self.assertIn(prog, msg)
            self.assertIn("[--foo FOO]", msg)
            self.assertIn("[--config-path CONFIG_PATH]", msg)
            self.assertIn("[--bar BAR]", msg)
            self.assertIn("configuration", msg.lower())
            self.assertIn("file", msg.lower())
            self.assertIn("class", msg.lower())
            self.assertIn(MyConfig.__name__, msg)

    def test_prefix_is_keyword_only(self):
        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            add_cli_options(ArgumentParser(), "foo", config_t=MyConfig)

    def test_with_prefix(self):
        prog = "my_program"
        parser = ArgumentParser(prog=prog)
        parser.add_argument("--foo")
        prefix = "cU5t0M_-pr3f1x"
        add_cli_options(parser, config_t=MyConfig, prefix=prefix)
        parser.add_argument("--bar")

        with self.subTest("Does not have default option"):
            with self.assertRaises(SystemExit):
                parser.parse_args(("--config-path", "whatever"))
                # TODO: Prevent stderr msg?

        with self.subTest("With path arg"):
            expected_path = "/a/b/c.txt"
            args = parser.parse_args(("--foo", "f00", f"--{prefix}-config-path", expected_path, "--bar=6aR"))
            self.assertEqual("f00", args.foo)
            self.assertEqual(expected_path, args.cU5t0M__pr3f1x_config_path)
            self.assertEqual("6aR", args.bar)

        with self.subTest("Without path arg"):
            args = parser.parse_args(("--foo", "f00", "--bar=6aR"))
            self.assertEqual("f00", args.foo)
            self.assertIsNone(args.cU5t0M__pr3f1x_config_path)
            self.assertEqual("6aR", args.bar)

        with self.subTest("Help"):
            ostream = StringIO()
            parser.print_help(ostream)
            msg = ostream.getvalue()
            self.assertIn(prog, msg)
            self.assertIn("[--foo FOO]", msg)
            self.assertIn(f"[--{prefix}-config-path CONFIG_PATH]", msg)
            self.assertIn("[--bar BAR]", msg)
            self.assertIn("configuration", msg.lower())
            self.assertIn("file", msg.lower())
            self.assertIn("class", msg.lower())
            self.assertIn(MyConfig.__name__, msg)

# TODO: Invalid prefixes
# TODO: Valid prefixes?
# TODO: Can add multiple
