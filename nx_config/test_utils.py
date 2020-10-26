from contextlib import contextmanager

# noinspection PyProtectedMember
from nx_config._core.naming_utils import mutable_section_attr as _mutable_attr
from nx_config.config import Config


@contextmanager
def mutable_config(config: Config):
    sections = tuple(getattr(config, s) for s in getattr(type(config), "__annotations__", {}))

    for section in sections:
        setattr(section, _mutable_attr, True)

    try:
        yield
    finally:
        for section in sections:
            setattr(section, _mutable_attr, False)
