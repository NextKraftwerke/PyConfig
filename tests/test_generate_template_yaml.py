from argparse import ArgumentParser
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from sys import stdout, stderr
from unittest import TestCase

from nx_config import Config, add_cli_options


class GenerateTemplateYAMLTestCase(TestCase):
    def test_empty_config(self):
        class MyConfig(Config):
            pass

        parser = ArgumentParser()
        add_cli_options(parser, config_t=MyConfig)

        with self.assertRaises(SystemExit) as ctx:
            with redirect_stdout(StringIO()) as out_stream:
                parser.parse_args(("--generate-config", "yaml"))

        xcp = ctx.exception
        if xcp.code != 0:
            print(out_stream.getvalue(), file=stdout)
            raise xcp

        self.assertEqual("", out_stream.getvalue())

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
