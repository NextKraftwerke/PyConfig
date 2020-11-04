from typing import NamedTuple, Callable, Any

ValidatingFunction = Callable[[Any, Any], None]


class Validator(NamedTuple):
    entry_name: str
