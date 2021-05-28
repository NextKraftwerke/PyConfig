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
            resolve_path_w_oracles(prefix=None, env_map={"CONFIG_PATH": str(expected)}),
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
                    resolve_path_w_oracles(prefix=prefix, env_map={f"{env_key_prefix}_CONFIG_PATH": str(expected)}),
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

        for prefix in ("hällo", "H.ELL.O", "HELL'o", "he##o", "HEL LO", "H\tO", "H\nO", "9to5", "-hello", "_HELLO"):
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
