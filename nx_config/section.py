from pathlib import Path
from typing import Any

# noinspection PyProtectedMember
from nx_config._core.naming_utils import (
    mutable_section_attr as _mutable_attr,
    internal_name as _internal_name,
)
# noinspection PyProtectedMember
from nx_config._core.section_meta import SectionMeta as _Meta


def _base_value2str(value: Any) -> str:
    if isinstance(value, str):
        return repr(value)
    elif isinstance(value, Path):
        return f"'{value}'"

    return str(value)


def _value2str(value: Any) -> str:
    if isinstance(value, frozenset):
        return "{" + ", ".join((_base_value2str(x) for x in value)) + "}"
    elif isinstance(value, tuple):
        return "(" + ", ".join((_base_value2str(x) for x in value)) + ")"

    return _base_value2str(value)


class ConfigSection(metaclass=_Meta):
    _nx_config_internal__root = True

    def __init__(self):
        setattr(self, _mutable_attr, False)

        for entry_name in getattr(type(self), "__annotations__", {}):
            entry = getattr(type(self), entry_name)
            setattr(self, _internal_name(entry_name), entry.default)

    def __str__(self):
        entry_names = getattr(type(self), "__annotations__", {}).keys()
        entries = ((x, _value2str(getattr(self, x))) for x in entry_names)
        attrs_str = ", ".join((f"{k}={v}" for k, v in entries))
        return f"{type(self).__name__}({attrs_str})"

    def __repr__(self):
        entry_names = getattr(type(self), "__annotations__", {}).keys()
        entries = ((x, repr(getattr(self, x))) for x in entry_names)
        attrs_str = "".join((f"    {k}={v},\n" for k, v in entries))
        return f"{type(self).__name__}(\n{attrs_str})"
