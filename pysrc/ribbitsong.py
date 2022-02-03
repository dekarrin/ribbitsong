from typing import Callable, Optional

class FieldDef:
    def __init__(self, name: str, type_conv: Optional[Callable[[Any], Any]] = None, default: Any = None):
        self.name = name
        self.type = type_conv
        self.default = default


class Model:
    def __init__(self):
        self.fields = {}
        
    def add_field(self, name: str, type_conv: Optional[Callable[[Any], Any]] = None, default: Any = None):
        if name in self.fields:
            raise ValueError("field named {!r} already exists".format(name))
        new_field = FieldDef(name, type_conv, default)
        self.fields[name] = new_field
        
        
class FlexibleSchema:
    """
    It's flexible because you can add fields after data is present.
    """
    
    def __init__(self, name: str, model: Optional[Model] = None):
        if model is None:
            model = DataModel()
            
        self.name = name
        self.model = model
        
    def insert_row(self, row: dict[str, Any]):
        full_row = {}
        for f in self.model:
            field = self.model.fields[f]
            full_row[field.name] = field.default
        
        for col in row:
            if col not in self.model.fields:
                raise ValueError("no field named {!r} exists in this schema. Add to model first.")
            field = self.model.fields[col]
            full_row[col] = field.type_conv(row[col])
            