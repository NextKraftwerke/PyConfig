from io import StringIO
from typing import Optional
from unittest import TestCase

from nx_config import SecretString, ConfigSection, Config, Format

# noinspection PyProtectedMember
from nx_config._core.fill_with_oracles import fill_config_w_oracles
from tests.typing_test_helpers import collection_type_holders


class SecretStringTestCase(TestCase):
    def test_secret_string_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            _ = SecretString()

        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            _ = SecretString("Hello")

        with self.assertRaises(TypeError):
            _ = SecretString.__new__(SecretString)

    def test_not_in_wrong_type_err_msg(self):
        secret = 1234

        class MySection(ConfigSection):
            entry: SecretString

        class MyConfig(Config):
            sec: MySection

        with self.assertRaises(Exception) as ctx:
            fill_config_w_oracles(
                MyConfig(),
                in_stream=StringIO(f"sec:\n  entry: {secret}\n"),
                fmt=Format.yaml,
                env_prefix=None,
                env_map={},
            )

        msg = str(ctx.exception)
        self.assertNotIn(str(secret), msg)

    def test_not_in_invalid_yaml_err_msg(self):
        secret = "[0ae133b59ad04211843179e0ae566a10"

        class MySection(ConfigSection):
            entry: SecretString

        class MyConfig(Config):
            sec: MySection

        with self.assertRaises(Exception) as ctx:
            fill_config_w_oracles(
                MyConfig(),
                in_stream=StringIO(f"sec:\n  entry: {secret}\n"),
                fmt=Format.yaml,
                env_prefix=None,
                env_map={},
            )

        msg = str(ctx.exception)
        self.assertNotIn(secret, msg)

    def test_not_in_default_secret_err_msg(self):
        secret = "0ae133b59ad04211843179e0ae566a10"
        int_secret = 1234

        with self.subTest("No collection"):
            with self.assertRaises(Exception) as ctx1:
                # noinspection PyUnusedLocal
                class MySection1(ConfigSection):
                    entry: SecretString = secret

            msg1 = str(ctx1.exception)
            self.assertNotIn(secret, msg1)

        with self.subTest("Optional"):
            with self.assertRaises(Exception) as ctx2:
                # noinspection PyUnusedLocal
                class MySection2(ConfigSection):
                    entry: Optional[SecretString] = secret

            msg2 = str(ctx2.exception)
            self.assertNotIn(secret, msg2)

        with self.subTest("Collection"):
            t = collection_type_holders[0].tuple
            with self.assertRaises(Exception) as ctx3:
                # noinspection PyUnusedLocal
                class MySection3(ConfigSection):
                    entry: t[SecretString, ...] = (secret,)

            msg3 = str(ctx3.exception)
            self.assertNotIn(secret, msg3)

        with self.subTest("String for collection"):
            t = collection_type_holders[0].tuple
            with self.assertRaises(Exception) as ctx4:
                # noinspection PyUnusedLocal
                class MySection4(ConfigSection):
                    entry: t[SecretString, ...] = secret

            msg4 = str(ctx4.exception)
            self.assertNotIn(secret, msg4)

        with self.subTest("Collection with wrong type element"):
            t = collection_type_holders[0].tuple
            with self.assertRaises(Exception) as ctx5:
                # noinspection PyUnusedLocal
                class MySection5(ConfigSection):
                    entry: t[SecretString, ...] = (int_secret,)

            msg5 = str(ctx5.exception)
            self.assertNotIn(str(int_secret), msg5)

        with self.subTest("No collection and wrong type"):
            with self.assertRaises(Exception) as ctx6:
                # noinspection PyUnusedLocal
                class MySection6(ConfigSection):
                    entry: SecretString = int_secret

            msg6 = str(ctx6.exception)
            self.assertNotIn(str(int_secret), msg6)
