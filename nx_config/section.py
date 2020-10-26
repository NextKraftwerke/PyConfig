# noinspection PyProtectedMember
from nx_config._core.naming_utils import (
    mutable_section_attr as _mutable_attr,
    internal_name as _internal_name,
)
# noinspection PyProtectedMember
from nx_config._core.section_meta import SectionMeta as _Meta


class ConfigSection(metaclass=_Meta):
    _nx_config_internal_root = True

    def __init__(self):
        setattr(self, _mutable_attr, False)

        for entry_name in getattr(type(self), "__annotations__", {}):
            entry = getattr(type(self), entry_name)
            setattr(self, _internal_name(entry_name), entry.default)
