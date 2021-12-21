from datetime import datetime
from typing import Optional
from unittest import TestCase
from uuid import UUID

from nx_config import (
    Config,
    ConfigSection,
    validate,
    URL,
    SecretString,
    ValidationError,
)
from nx_config.test_utils import update_section
from tests.typing_test_helpers import collection_type_holders


class EmptySection(ConfigSection):
    pass


class MutableConfigTestCase(TestCase):
    def test_cannot_be_imported_directly_from_nx_config(self):
        with self.assertRaises(ImportError):
            # noinspection PyUnresolvedReferences
            from nx_config import update_section

    def test_can_set_entries_with_test_util(self):
        class MySection(ConfigSection):
            my_entry: int
            my_entry_d: int = 42

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()
        self.assertIs(cfg.my_section.my_entry, MySection().my_entry)
        self.assertEqual(42, cfg.my_section.my_entry_d)

        update_section(cfg.my_section, my_entry=7, my_entry_d=99)

        self.assertEqual(7, cfg.my_section.my_entry)
        self.assertEqual(99, cfg.my_section.my_entry_d)

    def test_sections_are_immutable_after_test_util(self):
        class MySection(ConfigSection):
            my_entry: int = 42

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()

        update_section(cfg.my_section, my_entry=7)

        with self.assertRaises(AttributeError):
            cfg.my_section.my_entry = 123

    def test_wrong_key_raises_attr_error(self):
        class MySection(ConfigSection):
            my_entry: int = 42

        update_section(MySection(), my_entry=100)

        with self.assertRaises(AttributeError):
            update_section(MySection(), not_an_entry=100)

    def test_sections_are_immutable_after_exception_in_test_util(self):
        class MySection(ConfigSection):
            my_entry: int = 42

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()

        try:
            update_section(cfg.my_section, not_an_entry=100)
        except AttributeError:
            pass

        with self.assertRaises(AttributeError):
            cfg.my_section.my_entry = 123

    def test_can_have_different_config_instances(self):
        class MySection(ConfigSection):
            my_entry: int = 42

        class MyConfig(Config):
            my_section: MySection

        cfg1 = MyConfig()
        cfg2 = MyConfig()

        update_section(cfg1.my_section, my_entry=9)

        self.assertNotEqual(cfg2.my_section.my_entry, cfg1.my_section.my_entry)

    def test_does_validate_after_mutation(self):
        class MySection(ConfigSection):
            my_entry: int = 42

            @validate
            def will_never_pass(self):
                raise ValueError()

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()

        with self.assertRaises(ValueError):
            update_section(cfg.my_section)

    def test_uses_all_validators(self):
        class MySection(ConfigSection):
            my_entry: int = 42

            @validate
            def must_be_positive(self):
                if self.my_entry <= 0:
                    raise ValueError()

            @validate
            def must_be_even(self):
                if self.my_entry % 2 != 0:
                    raise ValueError()

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()

        update_section(cfg.my_section)
        update_section(cfg.my_section, my_entry=100)

        with self.assertRaises(ValueError):
            update_section(cfg.my_section, my_entry=-4)

        with self.assertRaises(ValueError):
            update_section(cfg.my_section, my_entry=101)

    def test_no_mutation_in_validators(self):
        class MySection(ConfigSection):
            my_entry: int = 42

            @validate
            def set_to_seven(self):
                self.my_entry = 7

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()

        with self.assertRaises(ValidationError) as ctx:
            update_section(cfg.my_section, my_entry=100)

        self.assertEqual(100, cfg.my_section.my_entry)

        msg = str(ctx.exception)
        self.assertIn("set", msg.lower())

    def test_cannot_assign_float_to_int(self):
        class MySection(ConfigSection):
            my_entry: int = 42

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()

        with self.assertRaises(TypeError) as ctx:
            update_section(cfg.my_section, my_entry=3.14)

        self.assertEqual(42, cfg.my_section.my_entry)

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("int", msg)
        self.assertIn("float", msg)
        self.assertIn("set", msg.lower())

    def test_cannot_assign_integer_string_to_int(self):
        class MySection(ConfigSection):
            my_entry: int = 42

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()

        with self.assertRaises(TypeError) as ctx:
            update_section(cfg.my_section, my_entry="100")

        self.assertEqual(42, cfg.my_section.my_entry)

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("int", msg)
        self.assertIn("str", msg)
        self.assertIn("set", msg.lower())

    def test_cannot_assign_none_to_int(self):
        class MySection(ConfigSection):
            my_entry: int = 42

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()

        with self.assertRaises(TypeError) as ctx:
            update_section(cfg.my_section, my_entry=None)

        self.assertEqual(42, cfg.my_section.my_entry)

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("int", msg)
        self.assertIn("NoneType", msg)
        self.assertIn("set", msg.lower())

    def test_can_assign_none_to_optional_int(self):
        class MySection(ConfigSection):
            my_entry: Optional[int] = 42

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()

        update_section(cfg.my_section, my_entry=None)
        self.assertIsNone(cfg.my_section.my_entry)

    def test_can_assign_value_to_optional_int(self):
        class MySection(ConfigSection):
            my_entry: Optional[int] = None

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()

        update_section(cfg.my_section, my_entry=42)
        self.assertEqual(42, cfg.my_section.my_entry)

    def test_type_check_comes_before_validators(self):
        class MySection(ConfigSection):
            my_entry: int = 42

            @validate
            def raise_value_error(self):
                raise ValueError()

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()

        with self.assertRaises(TypeError):
            update_section(cfg.my_section, my_entry=3.14)

    def test_can_assign_to_tuple_and_frozenset(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    my_tuple: tps.tuple[datetime, ...]
                    my_other_tuple: tps.tuple[float, ...] = (5.5,)
                    my_frozenset: tps.frozenset[UUID]
                    my_other_frozenset: tps.frozenset[URL] = frozenset(("abc.d.e",))

                class MyConfig(Config):
                    my_section: MySection

                cfg = MyConfig()

                new_tuple = (datetime(2020, 1, 1, 0, 44),)
                new_other_tuple = ()
                new_frozenset = frozenset((UUID(int=7), UUID(int=8)))
                new_other_frozenset = frozenset()

                update_section(
                    cfg.my_section,
                    my_tuple=new_tuple,
                    my_other_tuple=new_other_tuple,
                    my_frozenset=new_frozenset,
                    my_other_frozenset=new_other_frozenset,
                )

                self.assertEqual(new_tuple, cfg.my_section.my_tuple)
                self.assertEqual(new_other_tuple, cfg.my_section.my_other_tuple)
                self.assertEqual(new_frozenset, cfg.my_section.my_frozenset)
                self.assertEqual(new_other_frozenset, cfg.my_section.my_other_frozenset)

    def test_assigned_tuple_elements_must_have_base_type(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    my_entry: tps.tuple[int, ...]

                class MyConfig(Config):
                    my_section: MySection

                cfg = MyConfig()

                with self.assertRaises(TypeError) as ctx:
                    update_section(cfg.my_section, my_entry=(42, "43", 44, 45))

                msg = str(ctx.exception)
                self.assertIn("'my_entry'", msg)
                self.assertIn(str(tps.tuple[int, ...]), msg)
                self.assertIn("element", msg.lower())
                self.assertNotIn("default value", msg.lower())

    def test_cannot_assign_list_to_tuple(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    my_entry: tps.tuple[int, ...]

                class MyConfig(Config):
                    my_section: MySection

                cfg = MyConfig()

                with self.assertRaises(TypeError) as ctx:
                    update_section(cfg.my_section, my_entry=[])

                msg = str(ctx.exception)
                self.assertIn("'my_entry'", msg)
                self.assertIn(str(tps.tuple[int, ...]), msg)
                self.assertIn("list", msg)
                self.assertNotIn("default value", msg.lower())

    def test_cannot_assign_int_to_tuple(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    my_entry: tps.tuple[int, ...]

                class MyConfig(Config):
                    my_section: MySection

                cfg = MyConfig()

                with self.assertRaises(TypeError) as ctx:
                    update_section(cfg.my_section, my_entry=42)

                msg = str(ctx.exception)
                self.assertIn("'my_entry'", msg)
                self.assertIn(str(tps.tuple[int, ...]), msg)
                self.assertIn("int", msg)
                self.assertNotIn("default value", msg.lower())

    def test_cannot_assign_none_to_tuple(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    my_entry: tps.tuple[int, ...]

                class MyConfig(Config):
                    my_section: MySection

                cfg = MyConfig()

                with self.assertRaises(TypeError) as ctx:
                    update_section(cfg.my_section, my_entry=None)

                msg = str(ctx.exception)
                self.assertIn("'my_entry'", msg)
                self.assertIn(str(tps.tuple[int, ...]), msg)
                self.assertIn("NoneType", msg)
                self.assertNotIn("default value", msg.lower())

    def test_cannot_assign_tuple_to_frozenset(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    my_entry: tps.frozenset[int]

                class MyConfig(Config):
                    my_section: MySection

                cfg = MyConfig()

                with self.assertRaises(TypeError) as ctx:
                    update_section(cfg.my_section, my_entry=())

                msg = str(ctx.exception)
                self.assertIn("'my_entry'", msg)
                self.assertIn(str(tps.frozenset[int]), msg)
                self.assertIn("tuple", msg)
                self.assertNotIn("default value", msg.lower())

    def test_can_assign_str_to_secret_string(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    my_entry: SecretString
                    my_other_entry: tps.tuple[SecretString, ...] = ()

                class MyConfig(Config):
                    my_section: MySection

                cfg = MyConfig()

                secret = "abcdooo"
                secrets = ("1234000", "wwwww987")

                update_section(
                    cfg.my_section,
                    my_entry=secret,
                    my_other_entry=secrets,
                )

                self.assertEqual(secret, cfg.my_section.my_entry)
                self.assertEqual(secrets, cfg.my_section.my_other_entry)

    def test_cannot_assign_int_to_secret_string(self):
        class MySection(ConfigSection):
            my_entry: SecretString

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()

        with self.assertRaises(TypeError) as ctx:
            update_section(cfg.my_section, my_entry=42)

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("SecretString (a.k.a. str)", msg)
        self.assertIn("int", msg)
        self.assertNotIn("default value", msg.lower())

    def test_cannot_assign_int_to_url(self):
        class MySection(ConfigSection):
            my_entry: URL

        class MyConfig(Config):
            my_section: MySection

        cfg = MyConfig()

        with self.assertRaises(TypeError) as ctx:
            update_section(cfg.my_section, my_entry=42)

        msg = str(ctx.exception)
        self.assertIn("'my_entry'", msg)
        self.assertIn("URL (a.k.a. str)", msg)
        self.assertIn("int", msg)
        self.assertNotIn("default value", msg.lower())

    def test_cannot_assign_int_to_url_tuple(self):
        for tps in collection_type_holders:
            with self.subTest(types=tps):

                class MySection(ConfigSection):
                    my_entry: tps.tuple[URL, ...]

                class MyConfig(Config):
                    my_section: MySection

                cfg = MyConfig()

                with self.assertRaises(TypeError) as ctx:
                    update_section(cfg.my_section, my_entry=42)

                msg = str(ctx.exception)
                self.assertIn("'my_entry'", msg)
                self.assertIn("tuple[", msg.lower())
                self.assertIn("URL (a.k.a. str), ...]", msg)
                self.assertIn("int", msg)
                self.assertNotIn("default value", msg.lower())
