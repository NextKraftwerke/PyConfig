from argparse import ArgumentParser
from contextlib import redirect_stdout
from inspect import cleandoc
from io import StringIO
from sys import stdout
from typing import Union, Type, Optional
from unittest import TestCase

from nx_config import Config, add_cli_options


def assert_generates_equal(
    case: TestCase,
    fmt: str,
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

    with case.assertRaises(SystemExit) as ctx:
        with redirect_stdout(StringIO()) as out_stream:
            parser.parse_args((opt, fmt))

    xcp = ctx.exception
    if xcp.code != 0:
        print(out_stream.getvalue(), file=stdout)
        raise xcp

    expected = cleandoc(expected)
    if expected != "":
        expected += "\n"
    case.assertEqual(expected, out_stream.getvalue())
