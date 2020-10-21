from nx_config._core.section_entry import SectionEntry
from nx_config._core.unset import Unset

_special_section_keys = ("__module__", "__qualname__", "__annotations__")


class SectionMeta(type):
    def __new__(mcs, typename, bases, ns):
        if "_nx_config_internal_root" not in ns:
            if "__init__" in ns:
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

            for entry_name in entries:
                if entry_name.startswith("_"):
                    raise ValueError(
                        "Attributes of 'ConfigSection' subclass cannot start with underscores."
                    )

                default = ns.get(entry_name, Unset)
                ns[entry_name] = SectionEntry(default)

            special_keys = frozenset(entries).union(_special_section_keys)

            for k in ns:
                if k in special_keys:
                    continue

                raise ValueError(
                    f"Sections are not allowed to have attributes without type hints."
                    f" Non-conforming member: '{k}'"
                )

        ns["__slots__"] = ()
        return super().__new__(mcs, typename, bases, ns)
