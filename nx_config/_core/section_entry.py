from typing import Any

from nx_config._core.type_checks import ConfigTypeInfo
from nx_config._core.unset import Unset
from nx_config.secret_string import SecretString


def _check_default_value(value: Any, entry_name: str, type_info: ConfigTypeInfo):
    try:
        type_info.check_type(value)
    except TypeError as xcp:
        raise TypeError(f"Invalid default value for attribute '{entry_name}': {xcp}") from xcp

    if (
        (type_info.base is not SecretString) or
        (value is None) or
        ((type_info.collection is not None) and (len(value) == 0))
    ):
        return

    raise ValueError(
        f"Entries of base type 'SecretString' cannot have default values. Secrets should"
        f" never be hard-coded! Make sure you provide all necessary secrets through"
        f" (unversioned) configuration files and environment variables. Exceptions to this"
        f" rule: (1) Optional types can always have default value 'None'. (2) Collection"
        f" types can always have the corresponding empty collection as default value."
        f" Non-conforming attribute: '{entry_name}'"
    )


class SectionEntry:
    __slots__ = ("default", "entry_name", "_value_attribute", "type_info")

    def __init__(self, default: Any, entry_name: str, value_attribute: str, type_info: ConfigTypeInfo):
        self.default = default
        self.entry_name = entry_name
        self._value_attribute = value_attribute
        self.type_info = type_info

        if default is not Unset:
            _check_default_value(default, entry_name, type_info)

    def __get__(self, instance, owner):
        if instance is None:  # Called from the class
            return self

        return getattr(instance, self._value_attribute)

    def __set__(self, instance, value):
        raise AttributeError(
            "Setting config entries is not allowed. The contents of the config should be"
            " loaded at startup from defaults, configuration files and environment variables."
        )

    def _set(self, instance, value):
        try:
            self.type_info.check_type(value)
        except TypeError as xcp:
            raise TypeError(
                f"Error setting attribute '{self.entry_name}': {xcp}"
            ) from xcp

        setattr(instance, self._value_attribute, value)
