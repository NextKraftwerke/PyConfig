from unittest import TestCase

from nx_config import Config


class ConfigTestCase(TestCase):
    def test_config_subclass_init_forbidden(self):
        with self.assertRaises(ValueError):
            class MyConfig(Config):
                def __init__(self):
                    super(MyConfig, self).__init__()
