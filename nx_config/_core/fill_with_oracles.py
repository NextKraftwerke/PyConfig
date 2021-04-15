from datetime import datetime
from pathlib import Path
from typing import Mapping
from uuid import UUID

from dateutil.parser import parse as dateutil_parse

from nx_config._core.iteration_utils import get_annotations
from nx_config._core.naming_utils import internal_name
from nx_config._core.section_meta import run_validators
from nx_config._core.type_checks import ConfigTypeInfo
from nx_config._core.unset import Unset
from nx_config.config import Config
from nx_config.exceptions import ValidationError, IncompleteSectionError
from nx_config.section import ConfigSection


def _convert_string(value_str: str, type_info: ConfigTypeInfo):
    if type_info.base in (int, float, UUID, Path):
        return type_info.base(value_str)
    elif type_info.base is bool:
        return value_str == "True"
    elif type_info.base is datetime:
        return dateutil_parse(value_str)
    else:
        return value_str


def _check_all_entries_were_set(section: ConfigSection):
    for entry_name in get_annotations(section):
        if getattr(section, entry_name) is Unset:
            raise ValueError(f"Attribute '{entry_name}' has not been set and has no default value.")


def fill_config_w_oracles(cfg: Config, env_map: Mapping[str, str]):
    for section_name in get_annotations(cfg):
        section = getattr(cfg, section_name)

        for entry_name in get_annotations(section):
            env_key = f"{section_name.upper()}__{entry_name.upper()}"
            new_value = env_map.get(env_key)

            if new_value is not None:
                type_info = getattr(type(section), entry_name).type_info
                converted_new_value = _convert_string(new_value, type_info)
                setattr(section, internal_name(entry_name), converted_new_value)

        try:
            _check_all_entries_were_set(section)
        except ValueError as xcp:
            raise IncompleteSectionError(f"Incomplete section '{section_name}': {xcp}") from xcp

        try:
            run_validators(section)
        except Exception as xcp:
            raise ValidationError(f"Error validating section at the end of 'fill_config' call: {xcp}") from xcp
