class NxConfigError(Exception):
    pass


class ValidationError(NxConfigError, ValueError):
    pass


class IncompleteSectionError(NxConfigError, ValueError):
    pass
