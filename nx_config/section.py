# noinspection PyProtectedMember
from nx_config._core.entry_to_text import (
    entry2text as _entry2text,
    collection_type2masked_str as _col2masked_str,
    value2str as _val2str,
    collection_type2masked_repr as _col2masked_repr,
    value2repr as _val2repr,
)
# noinspection PyProtectedMember
from nx_config._core.naming_utils import (
    mutable_section_attr as _mutable_attr,
    internal_name as _internal_name,
    indentation_spaces as _indentation_spaces,
)
# noinspection PyProtectedMember
from nx_config._core.section_meta import SectionMeta as _Meta


class ConfigSection(metaclass=_Meta):
    _nx_config_internal__root = True

    def __init__(self):
        setattr(self, _mutable_attr, False)

        for entry_name in getattr(type(self), "__annotations__", {}):
            entry = getattr(type(self), entry_name)
            setattr(self, _internal_name(entry_name), entry.default)

    def __str__(self):
        entry_names = getattr(type(self), "__annotations__", {}).keys()
        entries = (
            (x, _entry2text(self, x, _col2masked_str, _val2str))
            for x in entry_names
        )
        attrs_str = ", ".join((f"{k}={v}" for k, v in entries))
        return f"{type(self).__name__}({attrs_str})"

    def __repr__(self):
        entry_names = getattr(type(self), "__annotations__", {}).keys()
        entries = (
            (x, _entry2text(self, x, _col2masked_repr, _val2repr))
            for x in entry_names
        )
        attrs_str = "".join((f"{_indentation_spaces}{k}={v},\n" for k, v in entries))
        return f"{type(self).__name__}(\n{attrs_str})"
