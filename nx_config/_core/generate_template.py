from typing import Type, TextIO

from nx_config._core.iteration_utils import get_annotations
from nx_config.config import Config


def generate_template(config_t: Type[Config], out_stream: TextIO):
    section_names = tuple(get_annotations(config_t))
    if section_names:
        out_stream.write(section_names[0] + ":")
