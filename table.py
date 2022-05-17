from typing import List
from parameter import Parameter


class Table:
    def __init__(self, name: str, params: List[Parameter]):
        self.name = name
        self.params = params
        self.param_number = len(params)
