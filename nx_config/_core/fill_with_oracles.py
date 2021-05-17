from datetime import datetime
from pathlib import Path
from typing import Mapping, Any, Iterable, Optional
from uuid import UUID

from dateutil.parser import parse as dateutil_parse

from nx_config._core.iteration_utils import get_annotations
from nx_config._core.naming_utils import internal_name
from nx_config._core.section_meta import run_validators
from nx_config._core.type_checks import ConfigTypeInfo
from nx_config._core.unset import Unset
from nx_config.config import Config
from nx_config.exceptions import ValidationError, IncompleteSectionError, ParsingError
from nx_config.section import ConfigSection

_truey_strings = frozenset(("True", "true", "TRUE", "Yes", "yes", "YES", "On", "on", "ON", "1"))
_falsey_strings = frozenset(("False", "false", "FALSE", "No", "no", "NO", "Off", "off", "OFF", "0"))
_upper_ascii_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_digits = "0123456789"
_env_prefix_first_char = _upper_ascii_letters + "_"
_env_prefix_chars = _env_prefix_first_char + _digits


def _convert_string_to_base(value_str: str, base: type) -> Any:
    if base in (int, float, Path, UUID):
        return base(value_str)
    elif base is bool:
        if value_str in _truey_strings:
            return True
        elif value_str in _falsey_strings:
            return False
        else:
            raise ValueError()
    elif base is datetime:
        return dateutil_parse(value_str)
    else:
        return value_str


def _convert_each_string_to_base(parts: Iterable[str], base: type) -> Iterable[Any]:
    for value_str in parts:
        try:
            yield _convert_string_to_base(value_str, base)
        except ValueError as xcp:
            raise ValueError(f"Invalid part: '{value_str}'; {xcp}") from xcp


def _convert_string(value_str: str, type_info: ConfigTypeInfo) -> Any:
    coll = type_info.collection
    base = type_info.base

    if coll is None:
        try:
            return _convert_string_to_base(value_str, base)
        except ValueError as xcp:
            raise ValueError(f"Cannot convert string '{value_str}' into {type_info}; {xcp}") from xcp
    else:
        parts = (x.strip() for x in value_str.split(","))
        try:
            # noinspection PyArgumentList
            return coll(_convert_each_string_to_base(parts, base))
        except ValueError as xcp:
            raise ValueError(f"Cannot convert string '{value_str}' into {type_info}; {xcp}") from xcp


def _check_all_entries_were_set(section: ConfigSection):
    for entry_name in get_annotations(section):
        if getattr(section, entry_name) is Unset:
            raise ValueError(f"Attribute '{entry_name}' has not been set and has no default value.")


def fill_config_w_oracles(cfg: Config, env_prefix: Optional[str], env_map: Mapping[str, str]):
    if env_prefix is None:
        pass
    else:
        if env_prefix == "":
            raise ValueError(
                f"Invalid empty prefix for configuration environment variables. If you do not want to use a custom"
                f" prefix use the (default) value None for 'env_prefix'."
            )
        if (env_prefix[0] not in _env_prefix_first_char) or any(x not in _env_prefix_chars for x in env_prefix[1:]):
            raise ValueError(
                f"Invalid prefix {repr(env_prefix)} for configuration environment variables. The only characters"
                f" allowed in the prefix are upper case ASCII letters '{_upper_ascii_letters}', numerical digits"
                f" '{_digits}' and underscores '_', with the additional restriction that the first character cannot"
                f" be a numerical digit."
            )

    for section_name in get_annotations(cfg):
        section = getattr(cfg, section_name)

        for entry_name in get_annotations(section):
            env_key = f"{section_name.upper()}__{entry_name.upper()}"
            new_value = env_map.get(env_key)

            if new_value is not None:
                type_info = getattr(type(section), entry_name).type_info

                try:
                    converted_new_value = _convert_string(new_value, type_info)
                except ValueError as xcp:
                    raise ParsingError(
                        f"Error parsing the value for section '{section_name}', attribute '{entry_name}'"
                        f" from environment variable '{env_key}': {xcp}"
                    ) from xcp

                setattr(section, internal_name(entry_name), converted_new_value)

        try:
            _check_all_entries_were_set(section)
        except ValueError as xcp:
            raise IncompleteSectionError(f"Incomplete section '{section_name}': {xcp}") from xcp

        try:
            run_validators(section)
        except Exception as xcp:
            raise ValidationError(
                f"Error validating section '{section_name}' at the end of 'fill_config' call: {xcp}"
            ) from xcp
