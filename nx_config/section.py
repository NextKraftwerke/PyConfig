# noinspection PyProtectedMember
from nx_config._core.section_meta import SectionMeta as _Meta
# noinspection PyProtectedMember
from nx_config._core.unset import Unset as _Unset


class ConfigSection(metaclass=_Meta):
    _nx_config_internal_root = None

    def __init__(self):
        for entry_name in getattr(type(self), "__annotations__", {}):
            setattr(self, entry_name, _Unset)
