class Parameter:
    def __init__(self, name: str, param_type: str, default: str = None):
        self.name = name
        self.type = param_type
        self.default = default
