from argparse import ArgumentParser
from pathlib import Path
from unittest import TestCase

from nx_config import resolve_config_path

# noinspection PyProtectedMember
from nx_config._core.path_with_oracles import resolve_path_w_oracles


class PathResolutionTestCase(TestCase):
    def test_defaults_to_none(self):
        self.assertIsNone(resolve_config_path())

    def test_default_env_var(self):
        expected = Path("../a/b/c.d")
        self.assertEqual(
            expected,
            resolve_path_w_oracles(
                prefix=None, cli_args=None, env_map={"CONFIG_PATH": str(expected)}
            ),
        )

    def test_env_var_prefix(self):
        expected = Path("/foo/bar.yaml")

        for prefix, env_key_prefix in (
            ("FOO_BAR", "FOO_BAR"),
            ("foo_bar", "FOO_BAR"),
            ("foo-bar", "FOO_BAR"),
            ("k", "K"),
            ("k-", "K_"),
            ("k2", "K2"),
            (
                "aBcDe_FGHIJ-klmno_PQRSt-UvwXY_Z0123-45678__9_",
                "ABCDE_FGHIJ_KLMNO_PQRST_UVWXY_Z0123_45678__9_",
            ),
        ):
            with self.subTest(prefix=prefix, env_key_prefix=env_key_prefix):
                self.assertEqual(
                    expected,
                    resolve_path_w_oracles(
                        prefix=prefix,
                        cli_args=None,
                        env_map={
                            "CONFIG_PATH": "not_expected",
                            f"{env_key_prefix}_CONFIG_PATH": str(expected),
                        },
                    ),
                )

    def test_invalid_prefix(self):
        with self.subTest(prefix=""):
            with self.assertRaises(ValueError) as ctx:
                resolve_config_path("")

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
                    resolve_config_path(prefix)

                msg = str(ctx.exception)
                self.assertIn(repr(prefix), msg)
                self.assertIn("abcdefghijklmnopqrstuvwxyz", msg)
                self.assertIn("ABCDEFGHIJKLMNOPQRSTUVWXYZ", msg)
                self.assertIn("-", msg)
                self.assertIn("_", msg)
                self.assertIn("0123456789", msg)
                self.assertIn("prefix", msg.lower())

    def test_use_argparser(self):
        expected = Path("/foo/bar.ini")
        option = "--config-path"
        parser = ArgumentParser()
        parser.add_argument(option, type=str)
        args = parser.parse_args((option, str(expected)))

        self.assertEqual(
            expected,
            resolve_config_path(cli_args=args),
        )

    def test_argparser_wo_value_for_option(self):
        option = "--config-path"
        parser = ArgumentParser()
        parser.add_argument(option, type=str)
        args = parser.parse_args(())

        with self.subTest("No env var"):
            self.assertIsNone(resolve_config_path(cli_args=args))

        with self.subTest("With env var"):
            expected = Path("/foo/bar.json")
            self.assertEqual(
                expected,
                resolve_path_w_oracles(
                    prefix=None, cli_args=args, env_map={"CONFIG_PATH": str(expected)}
                ),
            )

    def test_argparser_wo_option(self):
        parser = ArgumentParser()
        args = parser.parse_args(())

        with self.assertRaises(AttributeError) as ctx:
            resolve_config_path(cli_args=args)

        msg = str(ctx.exception)
        self.assertIn("'config_path'", msg)

    def test_cli_args_takes_precedence(self):
        expected = Path("/path/from/cli.yaml")
        option = "--config-path"
        parser = ArgumentParser()
        parser.add_argument(option, type=str)
        args = parser.parse_args((option, str(expected)))

        self.assertEqual(
            expected,
            resolve_path_w_oracles(
                prefix=None,
                cli_args=args,
                env_map={"CONFIG_PATH": "/path/from/env.var"},
            ),
        )

    def test_cli_args_is_keyword_only(self):
        option = "--abc-config-path"
        parser = ArgumentParser()
        parser.add_argument(option, type=str)
        args = parser.parse_args((option, "whatever"))

        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            resolve_config_path("abc", args)

    def test_argparser_with_prefix(self):
        expected = Path("foo/../bar.txt")
        prefix = "cU5t0M_-pr3f1x"
        option = f"--{prefix}-config-path"
        parser = ArgumentParser()
        parser.add_argument(option, type=str)

        with self.subTest("With CLI value"):
            args = parser.parse_args((option, str(expected)))

            self.assertEqual(
                expected,
                resolve_config_path(prefix, cli_args=args),
            )

        with self.subTest("Without CLI value"):
            args = parser.parse_args(())

            self.assertEqual(
                expected,
                resolve_path_w_oracles(
                    prefix=prefix,
                    cli_args=args,
                    env_map={
                        "CONFIG_PATH": "not_expected",
                        "CU5T0M__PR3F1X_CONFIG_PATH": str(expected),
                    },
                ),
            )

        with self.subTest("With nothing"):
            args = parser.parse_args(())
            self.assertIsNone(resolve_config_path(prefix, cli_args=args))

    def test_argparser_wo_option_with_prefix(self):
        option = "--config-path"
        parser = ArgumentParser()
        parser.add_argument(option, type=str)
        args = parser.parse_args((option, "whatever"))

        with self.assertRaises(AttributeError) as ctx:
            resolve_config_path("prfx", cli_args=args)

        msg = str(ctx.exception)
        self.assertIn("'prfx_config_path'", msg)
