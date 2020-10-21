from unittest import TestCase

from nx_config import SecretString


class SecretStringTestCase(TestCase):
    def test_secret_string_instance_is_just_str(self):
        for s in ("Hello", 42, 3.14, True, None, SecretString):
            self.assertIs(type(SecretString(s)), str)  # Stronger than 'isinstance'

    def test_secret_string_class_is_not_str(self):
        self.assertNotEqual(SecretString, str)

    def test_secret_string_is_a_type(self):
        self.assertIsInstance(SecretString, type)
