class NxConfigError(Exception):
    __slots__ = ()


class ValidationError(NxConfigError, ValueError):
    __slots__ = ()


class IncompleteSectionError(NxConfigError, ValueError):
    __slots__ = ()


class ParsingError(NxConfigError, ValueError):
    __slots__ = ()
