class SectionMeta(type):
    def __new__(mcs, typename, bases, ns):
        if ("_nx_config_internal_root" not in ns) and ("__init__" in ns):
            raise ValueError(
                "Subclass of 'ConfigSection' cannot define its own '__init__' method."
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

        return super().__new__(mcs, typename, bases, ns)
