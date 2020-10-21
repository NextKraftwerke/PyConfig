from nx_config._core.unset import Unset


class SectionEntry:
    def __get__(self, instance, owner):
        return Unset

    def __set__(self, instance, value):
        raise AttributeError(
            "Setting config entries is not allowed. The contents of the config should be"
            " loaded at startup from defaults, configuration files and environment variables."
        )
