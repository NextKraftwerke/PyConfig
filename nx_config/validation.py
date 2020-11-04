from typing import Callable

# noinspection PyProtectedMember
from nx_config._core.validator import (
    Validator as _Validator,
    ValidatingFunction as _ValidatingFunction,
)


def validate(entry_name: str) -> Callable[[_ValidatingFunction], _Validator]:
    def build_validator(validating_func: _ValidatingFunction) -> _Validator:
        _ = validating_func
        return _Validator(entry_name=entry_name)

    return build_validator
