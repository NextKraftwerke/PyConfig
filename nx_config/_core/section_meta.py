from inspect import isroutine, isclass
from typing import Any

from nx_config.secret_string import SecretString
from nx_config._core.naming_utils import mutable_section_attr, root_attr, internal_name, section_validators_attr
from nx_config._core.section_entry import SectionEntry
from nx_config._core.type_checks import ConfigTypeInfo
from nx_config._core.unset import Unset
from nx_config._core.validator import Validator

_special_section_keys = ("__module__", "__qualname__", "__annotations__", "__doc__", "__init__")


def _check_default_value(value: Any, entry_name: str, type_info: ConfigTypeInfo):
    try:
        type_info.check_type(value)
    except TypeError as xcp:
        raise TypeError(f"Invalid default value for attribute '{entry_name}': {xcp}")

    if (
        (type_info.base is not SecretString) or
        (value is None) or
        ((type_info.collection is not None) and (len(value) == 0))
    ):
        return

    raise ValueError(
        f"Entries of base type 'SecretString' cannot have default values. Secrets should"
        f" never be hard-coded! Make sure you provide all necessary secrets through"
        f" (unversioned) configuration files and environment variables. Exceptions to this"
        f" rule: (1) Optional types can always have default value 'None'. (2) Collection"
        f" types can always have the corresponding empty collection as default value."
        f" Non-conforming attribute: '{entry_name}'"
    )


class SectionMeta(type):
    def __new__(mcs, typename, bases, ns):
        is_root = ns.pop(root_attr, False)

        if ("__init__" in ns) and (not is_root):
            raise ValueError(
                "Subclass of 'ConfigSection' cannot define its own '__init__' method."
            )

        if "__slots__" in ns:
            raise ValueError(
                "Subclass of 'ConfigSection' cannot define its own '__slots__'."
            )

        entries = ns.get("__annotations__", {})

        if len({x.lower() for x in entries}) != len(entries):
            raise ValueError(
                "Names of entries within a 'ConfigSection' subclass must be case-insensitively"
                " unique because in some config file formats keys are parsed case-insensitively."
            )

        for entry_name, entry_type in entries.items():
            if entry_name.startswith("_"):
                raise ValueError(
                    f"Attributes of 'ConfigSection' subclass cannot start with underscores."
                    f" Non-conforming attribute: '{entry_name}'"
                )

            try:
                type_info = ConfigTypeInfo.from_type_hint(entry_type)
            except TypeError as xcp:
                raise TypeError(f"Unsupported type-hint for attribute '{entry_name}': {xcp}")

            default = ns.get(entry_name, Unset)

            if default is not Unset:
                _check_default_value(default, entry_name, type_info)

            ns[entry_name] = SectionEntry(default, internal_name(entry_name))

        special_keys = frozenset(entries).union(_special_section_keys)
        validators = []

        for k, v in ns.items():
            if isinstance(v, Validator):
                validators.append(v.wrapped)
            elif (k not in special_keys) and (not isroutine(v)) and (not isclass(v)):
                raise ValueError(
                    f"Sections are not allowed to have attributes without type hints."
                    f" You can add attributes with (supported) type hints (and optionally"
                    f" default values), as well as methods, nested types, type aliases and"
                    f" validators (i.e. methods with the '@validate' annotation)."
                    f" Non-conforming member: '{k}'"
                )

        ns[section_validators_attr] = tuple(validators)
        ns["__slots__"] = (mutable_section_attr, *(internal_name(e) for e in entries))
        return super().__new__(mcs, typename, bases, ns)
