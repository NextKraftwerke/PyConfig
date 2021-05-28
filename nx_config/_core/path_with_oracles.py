from pathlib import Path
from typing import Mapping, Optional


def resolve_path_w_oracles(env_map: Mapping[str, str]) -> Optional[Path]:
    try:
        return Path(env_map["CONFIG_PATH"])
    except KeyError:
        return None
