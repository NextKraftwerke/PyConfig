# noinspection PyProtectedMember
from nx_config._core.config_meta import ConfigMeta as _Meta
# noinspection PyProtectedMember
from nx_config._core.naming_utils import internal_name as _internal_name


class Config(metaclass=_Meta):
    _nx_config_internal_root = True

    def __init__(self):
        for section_name, section_type in getattr(type(self), "__annotations__", {}).items():
            setattr(self, _internal_name(section_name), section_type())
