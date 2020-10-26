_allowed_attributes = ("__module__", "__qualname__", "__annotations__")


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

        for attr in ns:
            if attr not in _allowed_attributes:
                raise ValueError(
                    f"Subclass of 'Config' can only have annotations for config sections."
                    f" No annotations of any other kind and no class attributes. Non-conforming"
                    f" attribute: '{attr}'"
                )

        return super().__new__(mcs, typename, bases, ns)
