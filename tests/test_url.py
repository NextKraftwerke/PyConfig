from unittest import TestCase

from nx_config import URL


class URLTestCase(TestCase):
    def test_url_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            _ = URL()

        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            _ = URL("https://www.abcdefg.com")

        with self.assertRaises(TypeError):
            _ = URL.__new__(URL)
