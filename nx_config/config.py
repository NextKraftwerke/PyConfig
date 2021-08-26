# noinspection PyProtectedMember
from nx_config._core.config_meta import ConfigMeta as _Meta
# noinspection PyProtectedMember
from nx_config._core.iteration_utils import get_annotations as _get_annotations
# noinspection PyProtectedMember
from nx_config._core.naming_utils import (
    internal_name as _internal_name,
    indentation_spaces as _indentation_spaces,
)


def _indent_new_lines(s: str) -> str:
    return s.replace("\n", f"\n{_indentation_spaces}")


class Config(metaclass=_Meta):
    """
    TODO
    """
    _nx_config_internal__root = True

    def __init__(self):
        for section_name, section_type in _get_annotations(self).items():
            setattr(self, _internal_name(section_name), section_type())

    def __str__(self):
        sections = ((x, getattr(self, x)) for x in _get_annotations(self))
        sections_str = ", ".join(f"{k}={v}" for k, v in sections)
        return f"{type(self).__name__}({sections_str})"

    def __repr__(self):
        sections = ((x, getattr(self, x)) for x in _get_annotations(self))
        sections_str = "".join(
            (f"{_indentation_spaces}{k}={_indent_new_lines(repr(v))},\n" for k, v in sections)
        )
        return f"{type(self).__name__}(\n{sections_str})"
