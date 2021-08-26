from sys import version_info
from typing import Any, Iterator

if version_info.minor < 7:
    from collections.abc import Mapping
    _SectionMappingBase = Mapping
else:
    from typing import Mapping
    _SectionMappingBase = Mapping[str, Any]

# noinspection PyProtectedMember
from nx_config._core.entry_to_text import (
    entry2text as _entry2text,
    collection_type2masked_str as _col2masked_str,
    value2str as _val2str,
    collection_type2masked_repr as _col2masked_repr,
    value2repr as _val2repr,
)
# noinspection PyProtectedMember
from nx_config._core.iteration_utils import get_annotations as _get_annotations
# noinspection PyProtectedMember
from nx_config._core.naming_utils import (
    internal_name as _internal_name,
    indentation_spaces as _indentation_spaces,
)
# noinspection PyProtectedMember
from nx_config._core.section_meta import SectionMeta as _Meta


class ConfigSection(_SectionMappingBase, metaclass=_Meta):
    """
    TODO
    """
    _nx_config_internal__root = True

    def __init__(self):
        for entry_name in _get_annotations(self):
            entry = getattr(type(self), entry_name)
            setattr(self, _internal_name(entry_name), entry.default)

    def __str__(self):
        entries = (
            (x, _entry2text(self, x, _col2masked_str, _val2str))
            for x in _get_annotations(self)
        )
        attrs_str = ", ".join((f"{k}={v}" for k, v in entries))
        return f"{type(self).__name__}({attrs_str})"

    def __repr__(self):
        entries = (
            (x, _entry2text(self, x, _col2masked_repr, _val2repr))
            for x in _get_annotations(self)
        )
        attrs_str = "".join((f"{_indentation_spaces}{k}={v},\n" for k, v in entries))
        return f"{type(self).__name__}(\n{attrs_str})"

    def __len__(self) -> int:
        return len(_get_annotations(self))

    def __iter__(self) -> Iterator[str]:
        return iter(_get_annotations(self))

    def __getitem__(self, k: str) -> Any:
        return getattr(self, k)
