from sys import version_info

_minor = version_info.minor

if _minor < 7:
    from typing import Optional, Sequence


    def get_origin(t: type) -> Optional[type]:
        origin = getattr(t, "__origin__", None)
        return getattr(origin, "__extra__", origin)


    def get_args(t: type) -> Sequence[type]:
        return getattr(t, "__args__", ())


elif _minor < 8:
    from typing import Optional, Sequence


    def get_origin(t: type) -> Optional[type]:
        return getattr(t, "__origin__", None)


    def get_args(t: type) -> Sequence[type]:
        return getattr(t, "__args__", ())


else:
    from typing import get_origin, get_args
