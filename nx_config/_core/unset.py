class UnsetType:
    __slots__ = ()

    def __init__(self):
        # Can only have 1 instance:
        type(self).__new__ = None

    def __repr__(self):
        return "Unset"


Unset = UnsetType()
