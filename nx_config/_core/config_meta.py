from inspect import isroutine, isclass

from nx_config._core.naming_utils import root_attr, internal_name
from nx_config.section import ConfigSection

_special_config_keys = ("__module__", "__qualname__", "__annotations__", "__doc__", "__init__")
_forbidden_default_section = "default"


def _internal_property(name: str) -> property:
    def getter(self):
        return getattr(self, name)

    # noinspection PyUnusedLocal
    def setter(self, value):
        raise AttributeError(
            "Setting config attributes is not allowed. The contents of the config should be"
            " loaded at startup from defaults, configuration files and environment variables."
        )

    return property(fget=getter, fset=setter)


class ConfigMeta(type):
    def __new__(mcs, typename, bases, ns):
        is_root = ns.pop(root_attr, False)

        if ("__init__" in ns) and (not is_root):
            raise ValueError(
                "Subclass of 'Config' cannot define its own '__init__' method."
            )

        if "__slots__" in ns:
            raise ValueError(
                "Subclass of 'Config' cannot define its own '__slots__'."
            )

        sections = ns.get("__annotations__", {})
        lower_sections = {x.lower() for x in sections}

        if len(lower_sections) != len(sections):
            raise ValueError(
                "Names of sections within a 'Config' subclass must be case-insensitively"
                " unique because in some config file formats keys are parsed case-insensitively."
            )

        if _forbidden_default_section in lower_sections:
            raise ValueError(
                f"The name '{_forbidden_default_section}' (or any case-variation thereof) is forbidden"
                f" for config sections because because it has a special meaning in INI files and that"
                f" behaviour is not supported by this library."
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

            ns[section_name] = _internal_property(internal_name(section_name))

        special_keys = frozenset(sections).union(_special_config_keys)

        for k, v in ns.items():
            if (k not in special_keys) and (not isroutine(v)) and (not isclass(v)):
                raise ValueError(
                    f"Attributes of 'Config' subclass must be sections, i.e., they must"
                    f" have type hints for subclasses of 'ConfigSection' (and no assigned value)."
                    f" You can also add methods and nested types."
                    f" Non-conforming member: '{k}'"
                )

        ns["__slots__"] = (internal_name(section) for section in sections)
        return super().__new__(mcs, typename, bases, ns)
