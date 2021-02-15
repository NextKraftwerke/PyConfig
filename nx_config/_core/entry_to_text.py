from pathlib import Path
from typing import Any, Optional, Type, Collection, Callable

from nx_config._core.unset import Unset
from nx_config.secret_string import SecretString

_secret_mask = "*****"


def _base_value2str(value: Any) -> str:
    if isinstance(value, str):
        return repr(value)
    elif isinstance(value, Path):
        return f"'{value}'"

    return str(value)


def value2str(value: Any) -> str:
    if isinstance(value, frozenset):
        return "{" + ", ".join((_base_value2str(x) for x in value)) + "}"
    elif isinstance(value, tuple):
        return "(" + ", ".join((_base_value2str(x) for x in value)) + ")"

    return _base_value2str(value)


def value2repr(value: Any) -> str:
    return repr(value)


def collection_type2masked_str(collection: Optional[Type[Collection]]) -> str:
    quoted_mask = f"'{_secret_mask}'"

    if collection is None:
        return quoted_mask

    if collection is frozenset:
        collection = set

    to_replace = "0," if collection is tuple else "0"
    return str(collection((0,))).replace(to_replace, f"{quoted_mask}, ...")


def collection_type2masked_repr(collection: Optional[Type[Collection]]) -> str:
    mask_repr = repr(_secret_mask)

    if collection is None:
        return mask_repr

    to_replace = "0," if collection is tuple else "0"
    # noinspection PyArgumentList
    return repr(collection((0,))).replace(to_replace, f"{mask_repr}, ...")


# noinspection PyUnresolvedReferences
def entry2text(
    section: "ConfigSection",
    entry_name: str,
    collection_type2masked_text: Callable[[Optional[Type[Collection]]], str],
    value2text: Callable[[Any], str],
) -> str:
    type_info = getattr(type(section), entry_name).type_info
    value = getattr(section, entry_name)

    if value is None:
        return "None"
    elif (
        (type_info.base is SecretString)
        and ((type_info.collection is None) or (len(value) != 0))
        and (value is not Unset)
    ):
        return collection_type2masked_text(type_info.collection)
    else:
        return value2text(value)
