from typing import Callable, Optional, Any, Union, List, Dict
import re

SerializedPrimitive = Optional[Union[int, str, float, bool]]
SerializedValue = Union[SerializedPrimitive, List['SerializedValue'], Dict[str, 'SerializedValue']]
SerializationVersion = 1
WhereClause = Optional[Callable[[Dict[str, Any]], bool]]

FieldValue = SerializedPrimitive
Row = Dict[str, FieldValue]

_field_types = {
    'int': int,
    'float': float,
    'str': str,
    'bool': bool
}




class FieldDef:
    def __init__(self, name: str, type: str = "str", default: Any = None):
        if type not in _field_types:
            raise ValueError("{!r} is not a valid field type".format(str(type)))
        if _identifier_re.match(name) is None:
            raise ValueError("{!r} is not a valid identifier".format(str(name)))
        self.name = name
        self._type_name = type
        self.type = _field_types[type]
        self.default = None if default is None else self.type(default)
        
    def to_dict(self) -> Dict[str, SerializedValue]:
        d = {
            'name': self.name,
            'type': self._type_name,
            'default': None,
        }
        if self.default is not None:
            d['default'] = str(self.default)
            
        return d
        
    def copy(self) -> 'FieldDef':
        return FieldDef(self.name, self.type, self.default)
    
    @staticmethod
    def from_dict(d: dict) -> 'FieldDef':
        if 'name' not in d:
            raise ValueError("missing key 'name'")
        if 'type' not in d:
            raise ValueError("missing key 'type'")
        if 'default' not in d:
            raise ValueError("missing key 'default'")
            
        name = str(d['name'])
        type_conv = str(d['type'])
        default = None
        if d['default'] is not None:
            default = str(d['default'])
        
        fd = FieldDef(name, type_conv, default)
        return fd


class Model:
    def __init__(self):
        self.fields = {}
        
    def to_dict(self) -> Dict[str, SerializedValue]:
        d = {"fields": list()}
        for f in self:
            d['fields'].append(self[f].to_dict())
            
        return d
        
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
        
    @staticmethod
    def from_dict(d: dict) -> 'Model':
        if 'fields' not in d:
            raise ValueError("missing key 'fields'")
        
        m = Model()
        
        for idx, f in enumerate(d['fields']):
            try:
                field = FieldDef.from_dict(f)
            except Exception as e:
                raise ValueError("fields[{:d}]: {:s}".format(idx, str(e)))
            if field.name in m:
                raise ValueError("field {!r} has duplicate entries".format(field.name))
            m.fields[field.name] = field
            
        return m
        
        
class FlexibleSchema:
    """
    It's flexible because you can add fields after data is present.
    """
    
    def __init__(self, name: str, model: Optional[Model] = None):
        if model is None:
            model = Model()
        
        if _identifier_re.match(name) is None:
            raise ValueError("{!r} is not a valid identifier".format(str(name)))
        self.name = name
        self.rows: List[Dict[str, FieldValue]] = []
        self._model = model
        
    def to_dict(self) -> Dict[str, SerializedValue]:
        d = {
            'version': SerializationVersion,
            'model': self._model.to_dict(),
            'data': self.rows,
            'name': self.name,
        }
        
        return d
        
    @staticmethod
    def from_dict(d: dict) -> 'FlexibleSchema':
        if 'version' not in d:
            raise ValueError("missing key 'version'")
            
        version = int(d['version'])
        if version > SerializationVersion:
            raise ValueError("version is {!r} but highest version supported is {!r}".format(version, SerializationVersion))
        
        if 'name' not in d:
            raise ValueError("missing key 'name'")
        if 'model' not in d:
            raise ValueError("missing key 'model'")
        if 'data' not in d:
            raise ValueError("missing key 'data'")
        
        name = str(d['name'])
        try:
            model = Model.from_dict(d['model'])
        except Exception as e:
            raise ValueError("model: {:s}".format(str(e)))
            
        fs = FlexibleSchema(name, model)
        
        # now add the rows via insert so that they are checked
        for r in d['data']:
            self.insert(r)
            
        return fs
    
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
        
        for f in self._model:
            if f not in new_model:
                drop_cols.append(f)
            elif hash(new_model[f].type) != hash(self._model[f].type):
                new_type_cols.append(f)
        for f in new_model:
            if f not in self._model:
                add_cols[f] = new_model[f].default
                
        # now apply to each existing row
        for r in self.rows:
            for col in new_type_cols:
                r[col] = model[col].type(str(r[col]))
            for col in drop_cols:
                del r[col]
            for col in add_col:
                r[col] = model[col].default
                
        # and set the new model
        self._model = model
            
        
    def insert(self, row: Row):
        full_row = {}
        for f in self._model:
            field = self._model[f]
            full_row[field.name] = field.default
        
        for col in row:
            if col not in self._model:
                raise ValueError("no field named {!r} exists in this schema. Add to model first.")
            field = self._model[col]
            full_row[col] = field.type_conv(row[col])
            
        self.rows.append(full_row)
            
    def select(self, where: WhereClause = None) -> List[Row]:
        """
        Select rows matching the whereclause.
        
        returns the rows selected.
        """
        if where is None:
            where = lambda r: True
            
        ret_rows = list()
        for r in self.rows:
            if where(r):
                ret_rows.append(r)
                
        return ret_rows
        
    def update(self, set_columns: Row, where: WhereClause = None) -> int:
        """
        Update rows matching the whereclause.
        
        returns number of rows updated.
        """
        if where is None:
            where = lambda r: True            

        for col in set_columns:
            if col not in self._model:
                raise ValueError("no field named {!r} exists in this schema. Add to model first.")
            
        updated = 0
        for r in self.rows:
            if where(r):
                for col in set_columns:
                    if col not in self._model:
                        raise ValueError("no field named {!r} exists in this schema. Add to model first.")
                    field = self._model[col]
                    r[col] = field.type_conv(set_columns[col])
                    updated += 1
                    
        return updated
            
    def drop(self, where: WhereClause = None) -> int:
        """
        Drop rows matching the whereclause.
        
        returns number of rows dropped.
        """
        if where is None:
            where = lambda r: True
        
        row_drops = list()
        for idx, r in enumerate(self.rows):
            if where(r):
                row_drops.append(idx)
                
        for idx in reversed(row_drops):
            del self.rows[idx]
            
        return len(row_drops)


class FlexibleStore:
    def __init__(self):
        self.schemas: Dict[str, FlexibleSchema] = {}
    
    def to_dict(self) -> Dict[str, SerializedValue]:
        d = {
            'version': SerializationVersion,
            'schemas': list()
        }
        for s in self:
            d['schemas'].append(self[s].to_dict())
        
        return d
        
    @staticmethod
    def from_dict(d: dict) -> 'FlexibleStore':
        if 'version' not in d:
            raise ValueError("missing key 'version'")
            
        version = int(d['version'])
        if version > SerializationVersion:
            raise ValueError("version is {!r} but highest version supported is {!r}".format(version, SerializationVersion))
        
        if 'schemas' not in d:
            raise ValueError("missing key 'schemas'")
            
        fs = FlexibleStore()
        
        for idx, f in enumerate(d['schemas']):
            try:
                schema = FlexibleSchema.from_dict(f)
            except Exception as e:
                raise ValueError("schemas[{:d}]: {:s}".format(idx, str(e)))
            if schema.name in fs:
                raise ValueError("schema {!r} has duplicate entries".format(field.name))
                
            fs.schemas[schema.name] = schema
            
        return fs
        
    def create_schema(self, schema: str, model: Optional[Model] = None):
        if schema in self:
            raise ValueError("schema named {!r} already exists".format(name))
        self.schemas[schema] = FlexibleSchema(schema, model)
        
    def drop_schema(self, schema: str) -> bool:
        """
        Return whether schema was dropped.
        """
        if schema not in self:
            return False
        else:
            del self.schemas[schema]
            return True
        
    def alter(self, schema: str, new_model: Model):
        if schema in self:
            raise ValueError("no such schema {!r}".format(schema))
            
        return self[schema].alter(new_model)
        
    def insert(self, schema: str, row: Row):
        if schema in self:
            raise ValueError("no such schema {!r}".format(schema))
            
        return self[schema].insert(row)
        
    def select(self, schema: str, where: WhereClause = None) -> List[Row]:
        if schema in self:
            raise ValueError("no such schema {!r}".format(schema))
            
        return self[schema].select(where)
        
    def update(self, schema: str, set_columns: Row, where: WhereClause = None) -> int:
        if schema in self:
            raise ValueError("no such schema {!r}".format(schema))
            
        return self[schema].update(set_columns, where)
        
    def drop(self, schema: str, where: WhereClause = None) -> int:
        if schema in self:
            raise ValueError("no such schema {!r}".format(schema))
            
        return self[schema].drop(where)
        
    def __getitem__(self, key):
        return self.schemas[key]
        
    def __delitem__(self, key):
        del self.schemas[key]
        
    def __len__(self):
        return len(self.schemas)
        
    def __iter__(self):
        return iter(self.schemas)
        
    def __contains__(self, item):
        return item in self.schemas
