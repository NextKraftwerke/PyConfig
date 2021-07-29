from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from typing import Type, Union, Optional, Tuple, FrozenSet
from unittest import TestCase

from nx_config import Config, add_cli_options, ConfigSection, SecretString
from tests.generate_template_test_helpers import assert_generates_equal


class GenerateTemplateINITestCase(TestCase):
    def assert_generates_equal(
        self,
        expected: str,
        parser_or_config_t: Union[ArgumentParser, Type[Config]],
        prefix: Optional[str] = None,
    ):
        assert_generates_equal(self, "ini", expected, parser_or_config_t, prefix)

    def test_empty_config(self):
        class MyConfig(Config):
            pass

        self.assert_generates_equal("", MyConfig)

    def test_empty_section(self):
        class EmptySection(ConfigSection):
            pass

        class MyConfig(Config):
            foo: EmptySection

        self.assert_generates_equal(
            """
            [foo]
            """,
            MyConfig,
        )

    def test_multiple_cli_options(self):
        class EmptySection(ConfigSection):
            pass

        class OneConfig(Config):
            one: EmptySection

        class OtherConfig(Config):
            other: EmptySection

        parser = ArgumentParser()
        add_cli_options(parser, config_t=OneConfig, prefix="one")
        add_cli_options(parser, config_t=OtherConfig, prefix="other")

        self.assert_generates_equal(
            """
            [one]
            """,
            parser,
            prefix="one",
        )
        self.assert_generates_equal(
            """
            [other]
            """,
            parser,
            prefix="other",
        )

    def test_multiple_empty_sections(self):
        class EmptySection(ConfigSection):
            pass

        class MyConfig(Config):
            foo: EmptySection
            bar: EmptySection
            baz: EmptySection

        self.assert_generates_equal(
            """
            [foo]
            
            [bar]
            
            [baz]
            """,
            MyConfig,
        )

    def test_with_entries_no_defaults(self):
        class MySection(ConfigSection):
            foo: int
            bar: bool

        class MyConfig(Config):
            buzz: MySection

        self.assert_generates_equal(
            """
            [buzz]
            foo =
            bar =
            """,
            MyConfig,
        )

    def test_full(self):
        class FirstSection(ConfigSection):
            foo: str
            bar: datetime
            baz: Optional[Tuple[Path, ...]] = None

        class SecondSection(ConfigSection):
            buzz: Optional[int] = 42
            huhu: FrozenSet[SecretString] = frozenset()
            foo: float
            hubba_hubba: SecretString

        class MyConfig(Config):
            some: FirstSection
            other: SecondSection
            again: FirstSection

        self.assert_generates_equal(
            """
            [some]
            foo =
            bar =
            #baz =
            
            [other]
            #buzz =
            #huhu =
            foo =
            hubba_hubba =
            
            [again]
            foo =
            bar =
            #baz =
            """,
            MyConfig,
        )
