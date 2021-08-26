from typing import Callable

# noinspection PyProtectedMember
from nx_config._core.validator import Validator as _Validator
from nx_config.section import ConfigSection


def validate(wrapped: Callable[[ConfigSection], None]) -> _Validator:
    """
    TODO
    """
    return _Validator(wrapped=wrapped)
