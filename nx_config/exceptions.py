class NxConfigError(Exception):
    """
    TODO
    """
    __slots__ = ()


class ValidationError(NxConfigError, ValueError):
    """
    TODO
    """
    __slots__ = ()


class IncompleteSectionError(NxConfigError, ValueError):
    """
    TODO
    """
    __slots__ = ()


class ParsingError(NxConfigError, ValueError):
    """
    TODO
    """
    __slots__ = ()
