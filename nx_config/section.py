# noinspection PyProtectedMember
from nx_config._core.section_meta import SectionMeta as _Meta


class ConfigSection(metaclass=_Meta):
    _nx_config_internal_root = None
