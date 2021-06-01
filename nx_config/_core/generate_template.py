from typing import Type, TextIO

from nx_config._core.iteration_utils import get_annotations
from nx_config._core.unset import Unset
from nx_config.config import Config


def generate_template(config_t: Type[Config], out_stream: TextIO):
    for section_name, section_cls in get_annotations(config_t).items():
        out_stream.write(f"{section_name}:\n")

        for entry_name in get_annotations(section_cls):
            has_default = getattr(section_cls, entry_name).default is not Unset
            prefix = "#" if has_default else ""
            out_stream.write(f"  {prefix}{entry_name}:\n")
