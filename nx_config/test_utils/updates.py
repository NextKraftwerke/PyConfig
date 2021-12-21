# noinspection PyProtectedMember
from nx_config._core.section_meta import run_validators as _run_validators
from nx_config.exceptions import ValidationError
from nx_config.section import ConfigSection


def update_section(section: ConfigSection, **kwargs):
    """
    TODO ...

    :param section:
    :param kwargs:
    """
    for entry_name, new_value in kwargs.items():
        entry = getattr(type(section), entry_name)
        # noinspection PyProtectedMember
        entry._set(section, new_value)

    try:
        _run_validators(section)
    except Exception as xcp:
        raise ValidationError(
            f"Error validating section at the end of 'test_utils.update_section' call: {xcp}"
        ) from xcp
