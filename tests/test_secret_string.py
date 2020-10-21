from unittest import TestCase

from nx_config import SecretString


class SecretStringTestCase(TestCase):
    def test_secret_string_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            _ = SecretString()

        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            _ = SecretString("Hello")

        with self.assertRaises(TypeError):
            _ = SecretString.__new__(SecretString)
