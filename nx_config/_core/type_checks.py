from datetime import datetime
from pathlib import Path
from typing import Tuple, Union, Optional, Type, Collection, NamedTuple, Any
from uuid import UUID

from nx_config._core.typing_utils import get_origin, get_args
from nx_config.secret_string import SecretString
from nx_config.url import URL

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

_NoneType = type(None)


def _get_optional_and_base(t: type) -> Tuple[bool, type]:
    if t.__module__ == "typing":
        origin = get_origin(t)
        args = get_args(t)

        if (
            (origin is Union) and
            (len(args) == 2) and
            any(x is _NoneType for x in args)
        ):
            # 'coverage' complains about not finishing the iteration on the
            # generator expression below. We only want to find the first occurence,
            # and the conditions above guarantee that there is one, hence 'no cover'.
            base = next(x for x in args if x is not _NoneType)  # pragma: no cover
            return True, base

    return False, t


def _get_collection_and_base(t: type) -> Tuple[Optional[Type[Collection]], type]:
    if t.__module__ in ("typing", "builtins"):
        origin = get_origin(t)
        args = get_args(t)

        if (
            isinstance(origin, type) and
            issubclass(origin, Collection) and
            (
                ((len(args) == 1) and (origin is not tuple)) or
                ((len(args) == 2) and (args[1] is Ellipsis) and (origin is tuple))
            )
        ):
            return origin, args[0]

    return None, t


def _nice_type_str(t: type):
    return t.__name__ if (t.__module__ != "typing" and len(get_args(t)) == 0) else str(t)


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
        nice_str = _nice_type_str(t)

        if (base not in _supported_base_types) or (collection not in (None, tuple, frozenset)):
            supported = ", ".join(
                sorted((x.__name__ for x in _supported_base_types), key=lambda x: x.lower())
            )
            raise TypeError(
                f"Type(-hint) '{nice_str}' is not supported for config entries. Allowed 'base' types:"
                f" {supported}. Allowed collections (where 'base' is one of the allowed base types):"
                f" typing.Tuple[base, ...], tuple[base, ...] (python 3.9+), typing.FrozenSet[base],"
                f" frozenset[base] (python 3.9+). Allowed optionals: typing.Optional[base] (where"
                f" 'base' is one of the allowed base types), typing.Optional[collection] (where"
                f" 'collection' is one of the allowed collection types). Note that bare collections,"
                f" such as tuple or typing.Tuple (i.e. without type-hints for their elements), are"
                f" not allowed."
            )

        full_str = nice_str.replace(
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
