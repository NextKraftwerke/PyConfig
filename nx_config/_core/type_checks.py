from datetime import datetime
from pathlib import Path
from typing import Tuple, Union, Optional, Type, Collection, NamedTuple, Any
from uuid import UUID

from nx_config.url import URL
from nx_config.secret_string import SecretString

_supported_base_types = frozenset((
    int,
    float,
    bool,
    str,
    datetime,
    UUID,
    Path,
    SecretString,
    URL,
))


def _get_optional_and_base(t: type) -> Tuple[bool, type]:
    try:
        origin = getattr(t, "__origin__")
        args = getattr(t, "__args__")
    except AttributeError:
        pass
    else:
        if (
            (t.__module__ == "typing") and
            (origin is Union) and
            (len(args) == 2) and
            isinstance(None, args[1])
        ):
            return True, args[0]

    return False, t


def _get_collection_and_base(t: type) -> Tuple[Optional[Type[Collection]], type]:
    try:
        origin = getattr(t, "__origin__")
        extra = getattr(origin, "__extra__")
        args = getattr(t, "__args__")
    except AttributeError:
        pass
    else:
        if (
            (t.__module__ == "typing") and
            issubclass(extra, Collection) and
            (
                ((len(args) == 1) and (extra is not tuple)) or
                ((len(args) == 2) and (args[1] is Ellipsis) and (extra is tuple))
            )
        ):
            return extra, args[0]

    return None, t


def _nice_type_str(t: type):
    return str(t) if t.__module__ == "typing" else t.__name__


def _expected_value_type(base: type) -> type:
    return str if base in (SecretString, URL) else base


class ConfigTypeInfo(NamedTuple):
    optional: bool
    collection: Optional[Type[Collection]]
    base: type
    full_str: str

    @classmethod
    def from_type_hint(cls, t: type) -> "ConfigTypeInfo":
        optional, base_or_collection = _get_optional_and_base(t)
        collection, base = _get_collection_and_base(base_or_collection)

        if base not in _supported_base_types:
            if collection is None:
                raise TypeError(
                    f"Type '{_nice_type_str(base)}' is not supported for config entries."
                )
            else:
                raise TypeError(
                    f"Type '{_nice_type_str(base)}' is not supported as the element-type for"
                    f" config entries that are collections."
                )
        if collection not in (None, tuple, frozenset):
            raise TypeError(
                f"Collection type '{_nice_type_str(collection)}' is not supported for config entries."
                f" You can represent sequences of values of the same type using 'tuple'"
                f" (with type-hint 'typing.Tuple[base_type, ...]'). You can also represent unordered sets"
                f" of unique values using 'frozenset' (with type-hint 'typing.FrozenSet[base_type]'). There's"
                f" currently no support for mappings."
            )

        full_str = _nice_type_str(t).replace(
            "SecretString", "SecretString (a.k.a. str)"
        ).replace(
            "URL", "URL (a.k.a. str)"
        )

        return ConfigTypeInfo(optional=optional, collection=collection, base=base, full_str=full_str)

    def __str__(self):
        return self.full_str

    def check_type(self, value: Any):
        if value is None:
            if self.optional:
                return
        elif self.collection is None:
            if isinstance(value, _expected_value_type(self.base)):
                return
        elif isinstance(value, self.collection):
            expected_element_type = _expected_value_type(self.base)
            if all(isinstance(x, expected_element_type) for x in value):
                return

            raise TypeError(
                f"Value must match the given type-hint. Expected '{self}' but not all elements"
                f" of the collection match the base type '{expected_element_type.__name__}'."
            )

        raise TypeError(
            f"Value must match the given type-hint. Expected '{self}',"
            f" got '{type(value).__name__}' instead."
        )

# TODO: Add support for different python versions:
#   - 3.6: Tuple[b, ...].__origin__==Tuple, Tuple.__extra__==tuple
#   - 3.8: Tuple[b, ...].__origin__==tuple, no __extra__ attribute
#   - 3.9: typing.Tuple deprecated, tuple[b, ...] supported, module is builtins
#   - Test typing.Tuple/FrozenSet[...] if python < 3.10. Test tuple/frozenset[...]
#   (same tests!) if python >= 3.9.
#   - Internally use imports from typing if python < 3.9 and from collections/builtins
#   if python >= 3.9 (except if necessary to support typing.Tuple/FrozenSet, but even
#   then only for python < 3.10 and then use collections/builtins for python >= 3.10).
