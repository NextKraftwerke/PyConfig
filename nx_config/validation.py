from typing import Callable

from nx_config.section import ConfigSection
# noinspection PyProtectedMember
from nx_config._core.validator import Validator as _Validator


def validate(wrapped: Callable[[ConfigSection], None]) -> _Validator:
    return _Validator(wrapped=wrapped)
