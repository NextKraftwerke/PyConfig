from typing import Mapping

from nx_config._core.iteration_utils import get_annotations
from nx_config._core.section_meta import run_validators
from nx_config._core.unset import Unset
from nx_config.config import Config
from nx_config.exceptions import ValidationError, IncompleteSectionError
from nx_config.section import ConfigSection


def _check_all_entries_were_set(section: ConfigSection):
    for entry_name in get_annotations(section):
        if getattr(section, entry_name) is Unset:
            raise ValueError(f"Attribute '{entry_name}' has not been set and has no default value.")


def fill_config_w_oracles(cfg: Config, env_map: Mapping[str, str]):
    for section_name in get_annotations(cfg):
        section = getattr(cfg, section_name)

        try:
            _check_all_entries_were_set(section)
        except ValueError as xcp:
            raise IncompleteSectionError(f"Incomplete section '{section_name}': {xcp}") from xcp

        try:
            run_validators(section)
        except Exception as xcp:
            raise ValidationError(f"Error validating section at the end of 'fill_config' call: {xcp}") from xcp
