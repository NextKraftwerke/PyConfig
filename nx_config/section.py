from pathlib import Path
from typing import Any, Optional, Type, Collection

# noinspection PyProtectedMember
from nx_config._core.naming_utils import (
    mutable_section_attr as _mutable_attr,
    internal_name as _internal_name,
    indentation_spaces as _indentation_spaces,
)
# noinspection PyProtectedMember
from nx_config._core.section_meta import SectionMeta as _Meta
# noinspection PyProtectedMember
from nx_config._core.unset import Unset as _Unset
from nx_config.secret_string import SecretString

_secret_mask = "*****"


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


def _collection2masked_str(collection: Optional[Type[Collection]]) -> str:
    quoted_mask = f"'{_secret_mask}'"

    if collection is None:
        return quoted_mask

    if collection is frozenset:
        collection = set

    to_replace = "0," if collection is tuple else "0"
    return str(collection((0,))).replace(to_replace, f"{quoted_mask}, ...")


def _value2repr(value: Any) -> str:
    return repr(value)


def _collection2masked_repr(collection: Optional[Type[Collection]]) -> str:
    mask_repr = repr(_secret_mask)

    if collection is None:
        return mask_repr

    to_replace = "0," if collection is tuple else "0"
    # noinspection PyArgumentList
    return repr(collection((0,))).replace(to_replace, f"{mask_repr}, ...")


class ConfigSection(metaclass=_Meta):
    _nx_config_internal__root = True

    def __init__(self):
        setattr(self, _mutable_attr, False)

        for entry_name in getattr(type(self), "__annotations__", {}):
            entry = getattr(type(self), entry_name)
            setattr(self, _internal_name(entry_name), entry.default)

    def _str_for_entry(self, name: str) -> str:
        type_info = getattr(type(self), name).type_info
        value = getattr(self, name)

        if value is None:
            return "None"
        elif (
            (type_info.base is SecretString)
            and ((type_info.collection is None) or (len(value) != 0))
            and (value is not _Unset)
        ):
            return _collection2masked_str(type_info.collection)
        else:
            return _value2str(value)

    def _repr_for_entry(self, name: str) -> str:
        type_info = getattr(type(self), name).type_info
        value = getattr(self, name)

        if value is None:
            return "None"
        elif (
            (type_info.base is SecretString)
            and ((type_info.collection is None) or (len(value) != 0))
            and (value is not _Unset)
        ):
            return _collection2masked_repr(type_info.collection)
        else:
            return _value2repr(value)

    def __str__(self):
        entry_names = getattr(type(self), "__annotations__", {}).keys()
        entries = ((x, self._str_for_entry(x)) for x in entry_names)
        attrs_str = ", ".join((f"{k}={v}" for k, v in entries))
        return f"{type(self).__name__}({attrs_str})"

    def __repr__(self):
        entry_names = getattr(type(self), "__annotations__", {}).keys()
        entries = ((x, self._repr_for_entry(x)) for x in entry_names)
        attrs_str = "".join((f"{_indentation_spaces}{k}={v},\n" for k, v in entries))
        return f"{type(self).__name__}(\n{attrs_str})"
