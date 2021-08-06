from configparser import ConfigParser
from datetime import datetime
from pathlib import Path
from typing import Mapping, Any, Iterable, Optional, TextIO
from uuid import UUID

# noinspection PyPackageRequirements
from dateutil.parser import parse as dateutil_parse
# noinspection PyPackageRequirements
from yaml import safe_load

from nx_config._core.iteration_utils import get_annotations
from nx_config._core.naming_utils import internal_name
from nx_config._core.section_meta import run_validators
from nx_config._core.type_checks import ConfigTypeInfo
from nx_config._core.unset import Unset
from nx_config.config import Config
from nx_config.exceptions import ValidationError, IncompleteSectionError, ParsingError
from nx_config.format import Format
from nx_config.section import ConfigSection

_truey_strings = frozenset(("True", "true", "TRUE", "Yes", "yes", "YES", "On", "on", "ON", "1"))
_falsey_strings = frozenset(("False", "false", "FALSE", "No", "no", "NO", "Off", "off", "OFF", "0"))
_upper_ascii_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_digits = "0123456789"
_env_prefix_first_char = _upper_ascii_letters + "_"
_env_prefix_chars = _env_prefix_first_char + _digits


def _convert_yaml_str_to_element(yaml_str: str, base: type) -> Any:
    try:
        return base(yaml_str)
    except ValueError as xcp:
        raise ValueError(f"Cannot convert string '{yaml_str}' into {base.__name__}: {xcp}") from xcp


def _convert_yaml(yaml_value: Any, type_info: ConfigTypeInfo) -> Any:
    base = type_info.base
    coll = type_info.collection

    if isinstance(yaml_value, str) and (base in (Path, UUID)):
        try:
            return base(yaml_value)
        except ValueError as xcp:
            raise ValueError(f"Cannot convert string '{yaml_value}' into {type_info}: {xcp}") from xcp
    elif isinstance(yaml_value, list) and (coll is not None):
        if base in (Path, UUID):
            try:
                # noinspection PyArgumentList
                return coll(_convert_yaml_str_to_element(x, base) if isinstance(x, str) else x for x in yaml_value)
            except ValueError as xcp:
                raise ValueError(f"Failed to convert list into {type_info}: {xcp}") from xcp
        # noinspection PyArgumentList
        return coll(yaml_value)
    else:
        return yaml_value


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

    if value_str == "":
        if type_info.optional:
            return None
        elif coll is not None:
            return coll()

    if coll is None:
        try:
            return _convert_string_to_base(value_str, base)
        except ValueError as xcp:
            raise ValueError(f"Cannot convert string '{value_str}' into {type_info}: {xcp}") from xcp
    else:
        parts = (x.strip() for x in value_str.split(","))
        try:
            # noinspection PyArgumentList
            return coll(_convert_each_string_to_base(parts, base))
        except ValueError as xcp:
            raise ValueError(f"Cannot convert string '{value_str}' into {type_info}: {xcp}") from xcp


def _check_all_entries_were_set(section: ConfigSection):
    for entry_name in get_annotations(section):
        if getattr(section, entry_name) is Unset:
            raise ValueError(f"Attribute '{entry_name}' has not been set and has no default value.")


def _check_env_prefix(prefix: str):
    if prefix == "":
        raise ValueError(
            f"Invalid empty prefix for configuration environment variables. If you don't want to use a custom"
            f" prefix, use None instead (default)."
        )

    if (prefix[0] not in _env_prefix_first_char) or any(x not in _env_prefix_chars for x in prefix[1:]):
        raise ValueError(
            f"Invalid prefix {repr(prefix)} for configuration environment variables. The only characters"
            f" allowed in the prefix are upper case ASCII letters '{_upper_ascii_letters}', numerical digits"
            f" '{_digits}' and underscores '_', with the additional restriction that the first character cannot"
            f" be a numerical digit."
        )


def fill_config_w_oracles(
    cfg: Config,
    in_stream: Optional[TextIO],
    fmt: Optional[Format],
    env_prefix: Optional[str],
    env_map: Mapping[str, str],
):
    if in_stream is None:
        in_map = None
        convert = None
    elif fmt is None:
        raise ValueError(
            "When filling a config object directly from a TextIO stream you must"
            " provide a corresponding nx_config.Format through the 'fmt' parameter."
        )
    elif fmt == Format.yaml:
        in_map = safe_load(in_stream)
        convert = _convert_yaml
    else:  # fmt == Format.ini
        in_map = ConfigParser()
        in_map.read_file(in_stream)
        convert = _convert_string

    if env_prefix is None:
        env_key_prefix = ""
    else:
        _check_env_prefix(env_prefix)
        env_key_prefix = f"{env_prefix}__"

    for section_name in get_annotations(cfg):
        section = getattr(cfg, section_name)

        if in_map is None:
            section_in_map = None
        else:
            # Cumbersome alternative to 'dict.get', necessary because
            # 'in_map' might be a 'configparser.RawConfigParser' and
            # 'configparser.RawConfigParser.get' doesn't get a whole
            # section but rather an option within a section.
            try:
                section_in_map = in_map[section_name]
            except KeyError:
                section_in_map = None

        try:
            for entry_name in get_annotations(section):
                env_key = f"{env_key_prefix}{section_name.upper()}__{entry_name.upper()}"
                env_value = env_map.get(env_key)

                if env_value is None:
                    if section_in_map is not None:
                        try:
                            in_map_value = section_in_map[entry_name]
                        except KeyError:
                            continue

                        entry = getattr(type(section), entry_name)
                        type_info = entry.type_info

                        try:
                            converted_new_value = convert(in_map_value, type_info)
                        except ValueError as xcp:
                            raise ValueError(
                                f"Error converting value for attribute '{entry_name}': {xcp}"
                            ) from xcp

                        # noinspection PyProtectedMember
                        entry._set(section, converted_new_value)
                else:
                    type_info = getattr(type(section), entry_name).type_info

                    try:
                        converted_new_value = _convert_string(env_value, type_info)
                    except ValueError as xcp:
                        raise ParsingError(
                            f"Error parsing the value for attribute '{entry_name}'"
                            f" from environment variable '{env_key}': {xcp}"
                        ) from xcp

                    setattr(section, internal_name(entry_name), converted_new_value)
        except Exception as xcp:
            raise type(xcp)(f"Error filling section '{section_name}': {xcp}") from xcp

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
