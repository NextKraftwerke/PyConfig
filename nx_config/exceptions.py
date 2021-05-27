class NxConfigError(Exception):
    __slots__ = ()


class ValidationError(NxConfigError, ValueError):
    __slots__ = ()


class IncompleteSectionError(NxConfigError, ValueError):
    __slots__ = ()


class ParsingError(NxConfigError, ValueError):
    __slots__ = ()


# TODO: Which exceptions do we want?
#   - Invalid type-hint?
#   - Wrong type value (default or from yaml)?
#   - Default secret?
#   - Wrong class syntax?
#   - Do we even want to keep the ones we already have? When would people use them?
#       When would people catch a config exception and react without crashing?
#       Isn't a config exception something that should just prevent an app from starting?
#       Specific exceptions can help with meaningful names, but we can get the same from
#       good error messages, can't we?
