from typing import Type, TextIO

from nx_config._core.iteration_utils import get_annotations
from nx_config._core.unset import Unset
from nx_config.config import Config
from nx_config.format import Format


def _generate_template_yaml(config_t: Type[Config], out_stream: TextIO):
    for section_name, section_cls in get_annotations(config_t).items():
        out_stream.write(f"{section_name}:\n")

        for entry_name in get_annotations(section_cls):
            has_default = getattr(section_cls, entry_name).default is not Unset
            prefix = "#" if has_default else ""
            out_stream.write(f"  {prefix}{entry_name}:\n")


def _generate_template_ini(config_t: Type[Config], out_stream: TextIO):
    for idx, (section_name, section_cls) in enumerate(get_annotations(config_t).items()):
        if idx != 0:
            out_stream.write("\n")

        out_stream.write(f"[{section_name}]\n")

        for entry_name in get_annotations(section_cls):
            has_default = getattr(section_cls, entry_name).default is not Unset
            prefix = "#" if has_default else ""
            out_stream.write(f"{prefix}{entry_name} =\n")


def generate_template(config_t: Type[Config], fmt: Format, out_stream: TextIO):
    if fmt == Format.yaml:
        _generate_template_yaml(config_t, out_stream)
    else:
        _generate_template_ini(config_t, out_stream)
