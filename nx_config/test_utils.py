# noinspection PyProtectedMember
from nx_config._core.naming_utils import (
    section_validators_attr as _section_validators_attr,
)
from nx_config.section import ConfigSection


def update_section(section: ConfigSection, **kwargs):
    for entry_name, new_value in kwargs.items():
        entry = getattr(type(section), entry_name)
        # noinspection PyProtectedMember
        entry._set(section, new_value)

    try:
        for validator in getattr(type(section), _section_validators_attr):
            validator(section)
    except AttributeError as xcp:
        raise AttributeError(
            f"Error validating section at the end of 'test_utils.update_section' call: {xcp}"
        ) from xcp
