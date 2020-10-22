class ConfigMeta(type):
    def __new__(mcs, typename, bases, ns):
        if "__init__" in ns:
            raise ValueError(
                "Subclass of 'Config' cannot define its own '__init__' method."
            )

        sections = ns.get("__annotations__", {})

        if len({x.lower() for x in sections}) != len(sections):
            raise ValueError(
                "Names of sections within a 'Config' subclass must be case-insensitively"
                " unique because in some config file formats keys are parsed case-insensitively."
            )

        for section_name in sections:
            if section_name.startswith("_"):
                raise ValueError(
                    "Attributes of 'Config' subclass cannot start with underscores."
                )

        return super().__new__(mcs, typename, bases, ns)
