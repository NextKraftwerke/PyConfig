from argparse import ArgumentParser
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime
from inspect import cleandoc
from io import StringIO
from pathlib import Path
from sys import stdout, stderr
from typing import Type, Union, Optional, Tuple, FrozenSet
from unittest import TestCase

from nx_config import Config, add_cli_options, ConfigSection, SecretString


class GenerateTemplateYAMLTestCase(TestCase):
    def assert_generates_equal(
        self,
        expected: str,
        parser_or_config_t: Union[ArgumentParser, Type[Config]],
        prefix: Optional[str] = None,
    ):
        if isinstance(parser_or_config_t, ArgumentParser):
            parser = parser_or_config_t
        else:
            parser = ArgumentParser()
            add_cli_options(parser, config_t=parser_or_config_t)

        if prefix is None:
            opt = "--generate-config"
        else:
            opt = f"--{prefix}-generate-config"

        with self.assertRaises(SystemExit) as ctx:
            with redirect_stdout(StringIO()) as out_stream:
                parser.parse_args((opt, "yaml"))

        xcp = ctx.exception
        if xcp.code != 0:
            print(out_stream.getvalue(), file=stdout)
            raise xcp

        expected = cleandoc(expected)
        if expected != "":
            expected += "\n"
        self.assertEqual(expected, out_stream.getvalue())

    def test_empty_config(self):
        class MyConfig(Config):
            pass

        self.assert_generates_equal("", MyConfig)

    def test_invalid_format(self):
        class MyConfig(Config):
            pass

        parser = ArgumentParser()
        add_cli_options(parser, config_t=MyConfig)

        with self.assertRaises(SystemExit) as ctx:
            with redirect_stderr(StringIO()) as err_stream:
                parser.parse_args(("--generate-config", "huhu"))

        xcp = ctx.exception
        if xcp.code != 2:
            print(err_stream.getvalue(), file=stderr)
            raise xcp

    def test_empty_section(self):
        class EmptySection(ConfigSection):
            pass

        class MyConfig(Config):
            foo: EmptySection

        self.assert_generates_equal(
            """
            foo:
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
            one:
            """,
            parser,
            prefix="one",
        )
        self.assert_generates_equal(
            """
            other:
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
            foo:
            bar:
            baz:
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
            buzz:
              foo:
              bar:
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
            some:
              foo:
              bar:
              #baz:
            other:
              #buzz:
              #huhu:
              foo:
              hubba_hubba:
            again:
              foo:
              bar:
              #baz:
            """,
            MyConfig,
        )
