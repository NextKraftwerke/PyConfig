from typing import Type

from nx_config.section import ConfigSection

_special_config_keys = ("__module__", "__qualname__", "__annotations__", "__doc__")


def _internal_property(section_type: Type[ConfigSection]) -> property:
    # noinspection PyUnusedLocal
    def getter(self):
        return section_type()

    # noinspection PyUnusedLocal
    def setter(self, value):
        raise AttributeError(
            "Setting config attributes is not allowed. The contents of the config should be"
            " loaded at startup from defaults, configuration files and environment variables."
        )

    return property(fget=getter, fset=setter)


class ConfigMeta(type):
    def __new__(mcs, typename, bases, ns):
        if "__init__" in ns:
            raise ValueError(
                "Subclass of 'Config' cannot define its own '__init__' method."
            )

        if "__slots__" in ns:
            raise ValueError(
                "Subclass of 'Config' cannot define its own '__slots__'."
            )

        sections = ns.get("__annotations__", {})

        if len({x.lower() for x in sections}) != len(sections):
            raise ValueError(
                "Names of sections within a 'Config' subclass must be case-insensitively"
                " unique because in some config file formats keys are parsed case-insensitively."
            )

        for section_name, section_type in sections.items():
            if section_name.startswith("_"):
                raise ValueError(
                    f"Attributes of 'Config' subclass cannot start with underscores."
                    f" Non-conforming attribute: '{section_name}'"
                )

            if section_name in ns:
                raise ValueError(
                    f"Section annotations cannot have an assigned value. Just write"
                    f" 'section_name: SectionType' and leave it with no value. The"
                    f" section instance will be automatically default-initialized."
                    f" Non-conforming attribute: '{section_name}'"
                )

            if not issubclass(section_type, ConfigSection):
                raise ValueError(
                    f"Types of annotated attributes in subclasses of 'Config' must be"
                    f" subclasses of 'ConfigSection'. Non-conforming attribute: '{section_name}'"
                )

            ns[section_name] = _internal_property(section_type)

        special_keys = frozenset(sections).union(_special_config_keys)

        for k in ns:
            if k in special_keys:
                continue

            raise ValueError(
                f"Subclass of 'Config' can only have annotations for config sections."
                f" No annotations of any other kind and no class attributes. Non-conforming"
                f" attribute: '{k}'"
            )

        ns["__slots__"] = ()
        return super().__new__(mcs, typename, bases, ns)
