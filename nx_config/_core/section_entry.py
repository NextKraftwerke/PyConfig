from typing import Any

from nx_config._core.naming_utils import mutable_section_attr


class SectionEntry:
    __slots__ = ("default", "_name")

    def __init__(self, default: Any, name: str):
        self.default = default
        self._name = name

    def __get__(self, instance, owner):
        if instance is None:  # Called from the class
            return self

        return getattr(instance, self._name)

    def __set__(self, instance, value):
        if not getattr(instance, mutable_section_attr):
            raise AttributeError(
                "Setting config entries is not allowed. The contents of the config should be"
                " loaded at startup from defaults, configuration files and environment variables."
            )

        setattr(instance, self._name, value)
