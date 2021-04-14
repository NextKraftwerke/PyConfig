from unittest import TestCase

from nx_config import NxConfigError, ValidationError


class ExceptionsTestCase(TestCase):
    def test_validation_error_is_nx_config_error(self):
        with self.assertRaises(NxConfigError):
            raise ValidationError()

    def test_validation_error_is_value_error(self):
        with self.assertRaises(ValueError):
            raise ValidationError()
