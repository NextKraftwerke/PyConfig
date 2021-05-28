from unittest import TestCase

from nx_config import resolve_config_path


class PathResolutionTestCase(TestCase):
    def test(self):
        self.assertIsNone(resolve_config_path())
