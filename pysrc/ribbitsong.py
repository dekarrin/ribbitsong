from typing import Callable, Optional

WhereClause = Optional[Callable[[dict[str, Any]], bool]]

class FieldDef:
    def __init__(self, name: str, type_conv: Optional[Callable[[Any], Any]] = None, default: Any = None):
        self.name = name
        self.type = type_conv
        self.default = default
        
    def copy(self) -> 'FieldDef':
        return FieldDef(self.name, self.type, self.default)


class Model:
    def __init__(self):
        self.fields = {}
        
    def copy(self) -> 'Model':
        m = Model()
        for f in self.fields:
            m.fields[f] = self.fields[f].copy()
        return m
        
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
            model = Model()
            
        self.name = name
        self.rows = []
        self._model = model
        
    @property
    def model(self) -> Model:
        return self._model.copy()
        
    def alter(self, new_model: Model):
        """
        Alter the model and update every single row to match.
        
        DROPPED COLUMNS WILL BE INSTANTLY DELETED.
        
        Altered type_convs are applied by calling str() on old data and then the new type_conv.
        """
        drop_cols = list()
        add_cols = dict()
        new_type_cols = list()
        
        for f in self._model.fields:
            if f not in new_model.fields:
                drop_cols.append(f)
            elif hash(new_model.fields[f].type) != hash(self._model.fields[f].type):
                new_type_cols.append(f)
        for f in new_model.fields:
            if f not in self._model.fields:
                add_cols[f] = new_model.fields[f].default
                
        # now apply to each existing row
                
        # and set the new model
        self._model = model
            
        
    def insert(self, row: dict[str, Any]):
        full_row = {}
        for f in self._model:
            field = self._model.fields[f]
            full_row[field.name] = field.default
        
        for col in row:
            if col not in self._model.fields:
                raise ValueError("no field named {!r} exists in this schema. Add to model first.")
            field = self._model.fields[col]
            full_row[col] = field.type_conv(row[col])
            
        self.rows.append(full_row)
            
    def drop(self, where: WhereClause = None) -> int:
        """
        Drop rows matching the whereclause.
        
        returns number of rows dropped.
        """
        if where is None:
            where = lambda(r): True
        
        row_drops = list()
        for idx, r in enumerate(self.rows):
            if where(r):
                row_drops.append(idx)
                
        for idx in reversed(row_drops):
            del self.rows[idx]
            
        return len(row_drops)
            
    def select(self, where: WhereClause = None) -> list[dict[str, Any]]:
        """
        Select rows matching the whereclause.
        
        returns the rows selected.
        """
        if where is None:
            where = lambda(r): True
            
        ret_rows = list()
        for r in self.rows:
            if where(r):
                ret_rows.append(r)
                
        return ret_rows
        
    def update(self, set_columns: dict[str, Any], where: WhereClause = None) -> int:
        """
        Update rows matching the whereclause.
        
        returns number of rows updated.
        """
        if where is None:
            where = lambda(r): True            

        for col in set_columns:
            if col not in self._model.fields:
                raise ValueError("no field named {!r} exists in this schema. Add to model first.")
            
        updated = 0
        for r in self.rows:
            if where(r):
                for col in set_columns:
                    if col not in self._model.fields:
                        raise ValueError("no field named {!r} exists in this schema. Add to model first.")
                    field = self._model.fields[col]
                    r[col] = field.type_conv(set_columns[col])
                    updated += 1
                    
        return updated