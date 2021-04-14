class NxConfigError(Exception):
    pass


class ValidationError(NxConfigError, ValueError):
    pass
