class SecretString:
    def __new__(cls, *args, **kwargs):
        return str(*args, **kwargs)
