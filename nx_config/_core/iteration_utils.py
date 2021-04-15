from typing import Any, Dict, Type


def get_annotations(obj: Any) -> Dict[str, Type]:
    return getattr(type(obj), "__annotations__", {})
