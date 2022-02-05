import re
from typing import Optional, Callable, Any, Tuple

from . import entry

_identifier_re = re.compile(r'[-A-Za-z_$][-A-Za-z0-9_$]*')

class Form:
    """
    Holds questions and data types for input. All input is returned as JSON
    documents.
    
    Limitations:
    
    * String fields can only accept the empty string if they have no default
    set and are not nullable.
    """
    
    def __init__(self, name: str = ""):
        self.name = name
        self.fields: dict[str, dict[str, Any]] = {}
        self.order: list[str] = []
        self._cursor = -1
        self._in_multivalue = False
        
    def add_field(self, name: str, type: Callable[[str], Any] = str, default: Optional[Any] = None, nullable: bool = False):
        """
        Add a field to the form. The user is prompted to fill in fields in the order
        that they were added.
        
        :param name: The name of the field. This must be unique within this Form.
        :param type: The type converter for data entered for the field. This is str by default.
        :param default: The default value if the user does not enter any data. This is not
        put through the type_conv function, so it should be the exact type that is desired for
        the field.
        :param nullable: Whether the field can be set to null.
        """
        if name in self.fields:
            raise ValueError("Field named {!r} already exists in this form".format(name))
        
        if _identifier_re.match(name) is None:
            raise ValueError("Field name is not a valid identifier: {!r}".format(name))
            
        f = {
            'field_type': 'simple',
            'name': name,
            'type': type,
            'default': default,
            'nullable': nullable,
        }
        
        self.fields[name] = f
        self.order.append(name)
        
    def add_object_field(self, name: str, nullable: bool = False) -> 'Form':
        """
        Add a field that is itself a series of properties. This can be used for making a
        particular field represent an entire object.
        
        Fields added to the returned Form are included when prompting to fill in the
        object.
        
        :param name: The name of the field. This must be unique within this Form.
        :param nullable: Whether the field can be set to null.
        """
        if name in self.fields:
            raise ValueError("Field named {!r} already exists in this form".format(name))
        
        if _identifier_re.match(name) is None:
            raise ValueError("Field name is not a valid identifier: {!r}".format(name))
        
        subform = Form(self.name + "." + name)
        
        f = {
            'field_type': 'object',
            'name': name,
            'form': subform,
            'nullable': nullable,
        }
        
        self.fields[name] = f
        self.order.append(name)
        return subform
        
    def remove(self, field_name: str):
        """
        Remove a field from this form.
        
        :param field_name: The name of the field to remove. If this field does not
        exist, no action is taken as the guarantee of this function will have been
        met.
        """
        if name in self.fields:
            del self.fields[name]
        
        self.order.remove(name)
        
    def fill(self) -> dict[str, Any]:
        """
        Prompt the user to fill out every field of the form and return a dict that
        contains the results.
        """
        if len(self) < 1:
            return {}
        
        filled = {}
        while self._has_more_prompts():
            path, value = self._ask([])
            
            cur = filled
            for idx, field_name in enumerate(path):
                if idx + 1 >= len(path):
                    # if this is the last path component, directly assign it to cur
                    cur[field_name] = value
                else:
                    # otherwise, this path component specifies a dict to be added
                    if field_name not in cur:
                        cur[field_name] = dict()
                    cur = cur[field_name]
                    
        self._reset()
        return filled
        
    def _reset(self):
        """
        Recursively set the cursor of this and all subforms to their initial positions.
        """
        self._cursor_to_start()
        self._in_multivalue = False
        
        for fname in self.fields:
            f = self.fields[fname]
            if f['field_type'] == 'object':
                f['form']._reset()
        
    def _has_more_prompts(self) -> bool:
        """
        Return whether the Form has more fields that it can ask about. The return
        value of this is equivalent to asking whether calling _ask without index or
        field would raise a ValueError due to the cursor being out of bounds.
        
        This method is recursive and considers any subforms (object fields) that this
        form is currently on.
        """
        if len(self.order) < 1:
            return False
        
        if self._cursor < len(self.order) - 1:
            return True
            
        if self._cursor > len(self.order) - 1:
            return False
            
        # we are at the last index but check to see if we are on a subform
        fname = self.order[self._cursor]
        if self.fields[fname]['field_type'] == 'object':
            subform = self.fields[fname]['form']
            return subform._has_more_prompts()
        
        
    def _ask(self, parents: list[str]) -> Tuple[list[str], Any]:
        """
        Ask the user to give data for a field. The user is prompted for the field
        that comes after the last one they were prompted for. If they haven't yet
        been prompted, the first field added to the form is used.
        
        :param parents: Parents of this field. Used for subform field identification.
        The top-level fields will have this be an empty list.
        :return: The full field path retrieved and the value that the user entered for it.
        :raises ValueError: If neither index or field are set to valid values, or if
        neither are set and a previous call to ask() resulted in the last field being
        prompted for.
        """
        if len(self.order) < 1:
            raise ValueError("no fields to ask about")
            
        # if cursor is currently pointing to a valid field,
        # check whether it is a subfield that has more questions
        # before incrementing
        if self._cursor > -1 and self._cursor < len(self.order):
            f = self.fields[self.order[self._cursor]]
            if f['field_type'] == 'object' and f['field']._has_more_prompts:
                index = self._cursor
            else:
                index = self._cursor + 1
        else:
            index = self._cursor + 1
        
        if index >= len(self.order):
            raise ValueError("no more questions to ask about; reset the form first".format(index))
            
        f = self.fields[self.order[index]]
        
        if f['field_type'] == 'simple':
            got_valid = False
            while not got_valid:
                full_path = '.'.join(parents + [f['name']])
                
                prompt = full_path
                if f['default'] is not None:
                    prompt += " (default: {!r})".format(f['default'])
  
                if f['nullable']:
                    prompt += "\n(Ctrl-D for explicit null)"
                    
                prompt += ": "
                    
                try:
                    str_input = input(prompt)
                except EOFError:
                    if f['nullable']:
                        value = None
                        got_valid = True
                        continue
                    else:
                        raise
                        
                if str_input == "":
                    if f['nullable'] or f['default'] is not None:
                        value = f['default']
                        got_valid = True
                        continue
                
                try:
                    value = f['type'](str_input)
                    got_valid = True
                except ValueError:
                    pass
                    
            self._cursor = index
            return list(parents + [f['name']]), value
        elif f['field_type'] == 'object':
            subform = f['form']
            # first if we havent asked anyfin and the subform entirely is nullable, prompt
            # to see if the user even wants to do a value
            
            full_path = '.'.join(parents + [f['name']])
            if f['nullable'] and subform._cursor == -1:
                if not entry.confirm("{:s} is nullable. Enter value for it?".format(full_path)):
                    subform._cursor_to_end()
                    return list(parents + f['name']), None
            
            subform_parents = list(parents)
            subform_parents.append(f['name'])
            return subform._ask(subform_parents)
        else:
            raise ValueError("unknown field_type: {!r}".format(f['field_type']))
            
    def _cursor_to_end(self):
        self._cursor = len(self) - 1
        
    def _cursor_to_start(self):
        self._cursor = -1
        
    def __len__(self) -> int:
        return len(self.fields)
        
        
        