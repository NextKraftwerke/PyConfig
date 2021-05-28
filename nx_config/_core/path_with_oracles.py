from pathlib import Path
from typing import Mapping, Optional

_base_env_key = "CONFIG_PATH"
_lower_ascii_letters = "abcdefghijklmnopqrstuvwxyz"
_digits = "0123456789"
_prefix_first_char = _lower_ascii_letters + _lower_ascii_letters.upper()
_prefix_chars = _prefix_first_char + _digits + "-_"


def _check_prefix(prefix: str):
    if prefix == "":
        raise ValueError(
            f"Invalid empty prefix for configuration path resolution. If you don't want to use a custom"
            f" prefix, use None instead (default)."
        )

    if (prefix[0] not in _prefix_first_char) or any(x not in _prefix_chars for x in prefix[1:]):
        raise ValueError(
            f"Invalid prefix {repr(prefix)} for configuration path resolution. The only characters"
            f" allowed in the prefix are lower case ASCII letters '{_lower_ascii_letters}', upper case"
            f" ASCII letters '{_lower_ascii_letters.upper()}', numerical digits '{_digits}', dashes '-'"
            f" and underscores '_', with the additional restriction that the first character must be a letter."
        )


def resolve_path_w_oracles(prefix: Optional[str], env_map: Mapping[str, str]) -> Optional[Path]:
    if prefix is None:
        env_key = _base_env_key
    else:
        _check_prefix(prefix)
        env_key = f"{prefix.upper().replace('-', '_')}_{_base_env_key}"

    try:
        return Path(env_map[env_key])
    except KeyError:
        return None
