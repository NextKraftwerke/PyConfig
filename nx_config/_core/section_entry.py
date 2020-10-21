from typing import Any


class SectionEntry:
    __slots__ = ("default",)

    def __init__(self, default: Any):
        self.default = default

    def __get__(self, instance, owner):
        return self.default

    def __set__(self, instance, value):
        raise AttributeError(
            "Setting config entries is not allowed. The contents of the config should be"
            " loaded at startup from defaults, configuration files and environment variables."
        )
