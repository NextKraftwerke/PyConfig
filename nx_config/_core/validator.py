from typing import NamedTuple, Callable


class Validator(NamedTuple):
    # noinspection PyUnresolvedReferences
    wrapped: Callable[["ConfigSection"], None]
