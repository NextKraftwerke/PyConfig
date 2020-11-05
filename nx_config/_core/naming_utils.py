def internal_name(name: str) -> str:
    return "_nx_config_internal_" + name


mutable_section_attr = internal_name("_mutable")
section_validators_attr = internal_name("_validators")
root_attr = internal_name("_root")
