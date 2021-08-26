class URL:
    """
    TODO

    ``URL`` cannot be instantiated. It is not meant to be used
    as an actual type but only as a type **hint** when declaring config
    entries within a config section. It allows the parser to handle those
    entries differently (e.g. by verifying that their values are valid URLs) and
    conveys their intended usage to the user.

    In the end, the actual type of the config entries is simply ``str``.
    """
    __new__ = None
