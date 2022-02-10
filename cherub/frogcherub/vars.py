from typing import Any

class GenericVar:
    def __init__(self, value: Any = None):
        self.value = value
        
    def set(self, value: Any):
        self.value = value
        
    def get(self) -> Any:
        return self.value