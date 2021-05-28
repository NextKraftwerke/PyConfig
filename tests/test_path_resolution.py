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
            resolve_path_w_oracles(env_map={"CONFIG_PATH": str(expected)}),
        )
