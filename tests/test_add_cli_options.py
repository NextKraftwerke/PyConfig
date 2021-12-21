from argparse import ArgumentParser
from contextlib import redirect_stderr
from io import StringIO
from sys import stderr
from unittest import TestCase

from nx_config import add_cli_options, Config, ConfigSection

format_choices = "{yaml,ini}"


class MyConfig(Config):
    class First(ConfigSection):
        entry_a: int
        entry_b: float = 0.1

    class Second(ConfigSection):
        entry_c: bool = True
        entry_d: str = ""

    first_sec: First
    second_sec: Second


class OtherConfig(Config):
    class First(ConfigSection):
        entry_a: str = "tab"

    first_sec: First


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
            args = parser.parse_args(
                ("--foo", "f00", "--config-path", expected_path, "--bar=6aR")
            )
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
            self.assertIn("[--bar BAR]", msg)
            self.assertIn("[--config-path CONFIG_PATH]", msg)
            self.assertIn("configuration", msg.lower())
            self.assertIn("file", msg.lower())
            self.assertGreaterEqual(msg.lower().count("class"), 2)
            self.assertGreaterEqual(msg.count(MyConfig.__name__), 2)
            self.assertIn(f"[--generate-config {format_choices}]", msg)
            self.assertIn("print", msg.lower())
            self.assertIn("standard", msg.lower())
            self.assertIn("output", msg.lower())
            self.assertIn("exit", msg.lower())

    def test_prefix_is_keyword_only(self):
        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            add_cli_options(ArgumentParser(), "foo", config_t=MyConfig)

    def test_with_prefix(self):
        prog = "my_program"

        for prefix in (
            "cU5t0M_-pr3f1x",
            "FOO_BAR",
            "foo_bar",
            "foo-bar",
            "k",
            "k-",
            "k2",
            "aBcDe_FGHIJ-klmno_PQRSt-UvwXY_Z0123-45678__9_",
        ):
            with self.subTest(prefix=prefix):
                args_attr = f"{prefix.replace('-', '_')}_config_path"
                parser = ArgumentParser(prog=prog)
                parser.add_argument("--foo")
                add_cli_options(parser, config_t=MyConfig, prefix=prefix)
                parser.add_argument("--bar")

                with self.subTest("Does not have default option"):
                    with self.assertRaises(SystemExit) as ctx:
                        with redirect_stderr(StringIO()) as err_stream:
                            parser.parse_args(("--config-path", "whatever"))

                    xcp = ctx.exception
                    if xcp.code != 2:
                        print(err_stream.getvalue(), file=stderr)
                        raise xcp

                with self.subTest("With path arg"):
                    expected_path = "/a/b/c.txt"
                    args = parser.parse_args(
                        (
                            "--foo",
                            "f00",
                            f"--{prefix}-config-path",
                            expected_path,
                            "--bar=6aR",
                        )
                    )
                    self.assertEqual("f00", args.foo)
                    self.assertEqual(expected_path, getattr(args, args_attr))
                    self.assertEqual("6aR", args.bar)

                with self.subTest("Without path arg"):
                    args = parser.parse_args(("--foo", "f00", "--bar=6aR"))
                    self.assertEqual("f00", args.foo)
                    self.assertIsNone(getattr(args, args_attr))
                    self.assertEqual("6aR", args.bar)

                with self.subTest("Help"):
                    ostream = StringIO()
                    parser.print_help(ostream)
                    msg = ostream.getvalue()
                    self.assertIn(prog, msg)
                    self.assertIn("[--foo FOO]", msg)
                    self.assertIn("[--bar BAR]", msg)
                    self.assertIn(f"[--{prefix}-config-path CONFIG_PATH]", msg)
                    self.assertIn("configuration", msg.lower())
                    self.assertIn("file", msg.lower())
                    self.assertGreaterEqual(msg.lower().count("class"), 2)
                    self.assertGreaterEqual(msg.count(MyConfig.__name__), 2)
                    self.assertIn(f"[--{prefix}-generate-config {format_choices}]", msg)
                    self.assertIn("print", msg.lower())
                    self.assertIn("standard", msg.lower())
                    self.assertIn("output", msg.lower())
                    self.assertIn("exit", msg.lower())

    def test_invalid_prefixes(self):
        with self.subTest(prefix=""):
            with self.assertRaises(ValueError) as ctx:
                add_cli_options(ArgumentParser(), config_t=MyConfig, prefix="")

            msg = str(ctx.exception)
            self.assertIn("empty", msg.lower())
            self.assertIn("default", msg.lower())
            self.assertIn("prefix", msg.lower())
            self.assertIn("None", msg)

        for prefix in (
            "hällo",
            "H.ELL.O",
            "HELL'o",
            "he##o",
            "HEL LO",
            "H\tO",
            "H\nO",
            "9to5",
            "-hello",
            "_HELLO",
        ):
            with self.subTest(prefix=prefix):
                with self.assertRaises(ValueError) as ctx:
                    add_cli_options(ArgumentParser(), config_t=MyConfig, prefix=prefix)

                msg = str(ctx.exception)
                self.assertIn(repr(prefix), msg)
                self.assertIn("abcdefghijklmnopqrstuvwxyz", msg)
                self.assertIn("ABCDEFGHIJKLMNOPQRSTUVWXYZ", msg)
                self.assertIn("-", msg)
                self.assertIn("_", msg)
                self.assertIn("0123456789", msg)
                self.assertIn("prefix", msg.lower())

    def test_add_multiple(self):
        prog = "my_program"
        parser = ArgumentParser(prog=prog)
        parser.add_argument("--foo")
        add_cli_options(parser, config_t=MyConfig)
        parser.add_argument("--bar")
        add_cli_options(parser, config_t=OtherConfig, prefix="other")
        add_cli_options(parser, config_t=MyConfig, prefix="same")
        add_cli_options(parser, config_t=OtherConfig, prefix="other_again")
        parser.add_argument("--baz")

        with self.subTest("Path arg"):
            expected_path_none = "/a/b/c.txt"
            expected_path_other = "a.b"
            expected_path_same = "../c.json"
            args = parser.parse_args(
                (
                    "--other-config-path",
                    expected_path_other,
                    "--foo",
                    "f00",
                    "--same-config-path",
                    expected_path_same,
                    "--config-path",
                    expected_path_none,
                    "--bar=6aR",
                )
            )
            self.assertEqual("f00", args.foo)
            self.assertEqual("6aR", args.bar)
            self.assertIsNone(args.baz)
            self.assertEqual(expected_path_none, args.config_path)
            self.assertEqual(expected_path_other, args.other_config_path)
            self.assertEqual(expected_path_same, args.same_config_path)
            self.assertIsNone(args.other_again_config_path)

        with self.subTest("Help"):
            ostream = StringIO()
            parser.print_help(ostream)
            msg = ostream.getvalue()
            self.assertIn(prog, msg)
            self.assertIn("[--foo FOO]", msg)
            self.assertIn("[--bar BAR]", msg)
            self.assertIn("[--baz BAZ]", msg)
            self.assertIn("[--config-path CONFIG_PATH]", msg)
            self.assertIn("[--other-config-path CONFIG_PATH]", msg)
            self.assertIn("[--same-config-path CONFIG_PATH]", msg)
            self.assertIn("[--other_again-config-path CONFIG_PATH]", msg)
            self.assertGreaterEqual(msg.lower().count("configuration"), 4)
            self.assertGreaterEqual(msg.lower().count("file"), 4)
            self.assertGreaterEqual(msg.lower().count("class"), 8)
            self.assertGreaterEqual(msg.count(MyConfig.__name__), 4)
            self.assertGreaterEqual(msg.count(OtherConfig.__name__), 4)
            self.assertIn(f"[--generate-config {format_choices}]", msg)
            self.assertIn(f"[--other-generate-config {format_choices}]", msg)
            self.assertIn(f"[--same-generate-config {format_choices}]", msg)
            self.assertIn(f"[--other_again-generate-config {format_choices}]", msg)
            self.assertGreaterEqual(msg.lower().count("print"), 4)
            self.assertGreaterEqual(msg.lower().count("standard"), 4)
            self.assertGreaterEqual(msg.lower().count("output"), 4)
            self.assertGreaterEqual(msg.lower().count("exit"), 4)
