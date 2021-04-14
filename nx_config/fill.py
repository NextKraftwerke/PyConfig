# noinspection PyProtectedMember
from nx_config._core.section_meta import run_validators as _run_validators
# noinspection PyProtectedMember
from nx_config._core.unset import Unset as _Unset
from nx_config.config import Config
from nx_config.exceptions import ValidationError
from nx_config.section import ConfigSection


def _check_all_entries_were_set(section: ConfigSection):
    for entry_name in getattr(type(section), "__annotations__", {}):
        if getattr(section, entry_name) is _Unset:
            raise ValueError(f"Attribute '{entry_name}' has not been set and has no default value.")


def fill_config(cfg: Config):
    for section_name in getattr(type(cfg), "__annotations__", {}):
        section = getattr(cfg, section_name)

        try:
            _check_all_entries_were_set(section)
        except ValueError as xcp:
            raise ValueError(f"Incomplete section '{section_name}': {xcp}") from xcp

        try:
            _run_validators(section)
        except Exception as xcp:
            raise ValidationError(f"Error validating section at the end of 'fill_config' call: {xcp}") from xcp
