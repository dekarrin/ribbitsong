import re
from typing import Optional, Callable, Any, Tuple, Dict, List
import uuid

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
        self.fields: Dict[str, Dict[str, Any]] = {}
        self.order: List[str] = []
        self._cursor = -1
        self._in_multivalue = False
        self._multivalue_index = -1
        
    def add_auto_uuid_field(self, name: str, entry_hook: Optional[Callable[[Any], Any]] = None):
        """
        Add a field whose value is automatically filled in with an auto-generated type 4 UUID.
        """
        if name in self.fields:
            raise ValueError("Field named {!r} already exists in this form".format(name))
        
        if _identifier_re.match(name) is None:
            raise ValueError("Field name is not a valid identifier: {!r}".format(name))
            
        f = {
            'field_type': 'autouuid',
            'name': name,
            'nullable': False,
            'multivalue': False,
            'entry_hook': entry_hook
        }
        
        self.fields[name] = f
        self.order.append(name)
        
    def add_field(
        self,
        name: str,
        type: Callable[[str], Any] = str,
        default: Optional[Any] = None,
        nullable: bool = False,
        multivalue: bool = False,
        sentinel: str = "done",
        default_last: bool = False,
        entry_hook: Optional[Callable[[Any], Any]] = None
    ):
        """
        Add a field to the form. The user is prompted to fill in fields in the order
        that they were added.
        
        :param name: The name of the field. This must be unique within this Form.
        :param type: The type converter for data entered for the field. This is str by default.
        :param default: The default value if the user does not enter any data. This is not
        put through the type_conv function, so it should be the exact type that is desired for
        the field. Alternatively, this can be a Callable that takes no arguments and produces
        a value; in this case, it will be called for the default value every time one is needed.
        :param nullable: Whether the field can be set to null.
        :param multivalue: Marks the field as multivalued (list-valued). When set to
        True, then during form filling the user is prompted for multiple values for this field
        until the sentinel value is entered. A multivalue field is represented by a non-nullable
        array, and the 'nullable' parameter refers to whether it accepts null values as members
        of the list.
        :param sentinel: This is the value that the user must enter to terminate a multivalue
        entry.
        :param default_last: Use the last entered value as the default. If this is set, 'default'
        is used only for the initial default.
        :param entry_hook: Called with the entered value whenever one is entered.
        """
        if name in self.fields:
            raise ValueError("Field named {!r} already exists in this form".format(name))
        
        if _identifier_re.match(name) is None:
            raise ValueError("Field name is not a valid identifier: {!r}".format(name))
            
        if multivalue:
            if sentinel == "":
                raise ValueError("sentinel cannot be an empty string for multivalued form fields.")
            
        # swap in a custom bool handler
        if type == bool:
            def bool_conv(s: str) -> bool:
                s = s.lower()
                if s == "yes" or s == "y" or s == "true" or s == "t" or s == 1 or s == "on":
                    return True
                elif s == "no" or s == "n" or s == "false" or s == "f" or s == 0 or s == "off":
                    return False
                else:
                    raise ValueError("value must yes or no")
            type = bool_conv
            
        f = {
            'field_type': 'simple',
            'name': name,
            'type': type,
            'default': default,
            'nullable': nullable,
            'multivalue': multivalue,
            'sentinel': sentinel,
            'default_last_entered': default_last,
            'entry_hook': entry_hook
        }
        
        self.fields[name] = f
        self.order.append(name)
        
    def add_choice_field(
        self,
        name: str,
        choices: List[str],
        default: Optional[Any] = None,
        nullable: bool = False,
        multivalue: bool = False,
        sentinel: str = "done",
    ):
        """Syntactic sugar for adding a str-type field that only allows certain values."""        
        if multivalue and sentinel in choices:
            raise ValueError("sentinel {!r} must not be present in choices list of multivalued choice field".format(sentinel))
        if default is not None and default not in choices:
            raise ValueError("default value {!r} must be present in choices list of choice field".format(sentinel))
        
        choices = list(choices)  # prevent caller from mutating this list
        def choice_checker(value: str) -> str:
            if value not in choices:
                msg = "Value must be one of: "
                msg += ','.join(repr(c) for c in choices)
                raise ValueError(msg)
            return value
            
        return self.add_field(name, choice_checker, default, nullable, multivalue, sentinel)
        
    def add_object_field(self, name: str, nullable: bool = False, multivalue: bool = False) -> 'Form':
        """
        Add a field that is itself a series of properties. This can be used for making a
        particular field represent an entire object.
        
        Fields added to the returned Form are included when prompting to fill in the
        object.
        
        :param name: The name of the field. This must be unique within this Form.
        :param nullable: Whether the field can be set to null.
        :param multivalued: Whether this field's value is a list of the given type. The user is prompted
        for values until they type the sentinel.
        :param multivalue: Marks the field as multivalued (list-valued). When set to
        True, then during form filling the user is prompted for multiple values for this field
        until the sentinel value is entered. A multivalue field is represented by a non-nullable
        array, and the 'nullable' parameter refers to whether it accepts null values as members
        of the list.
        """
        if name in self.fields:
            raise ValueError("Field named {!r} already exists in this form".format(name))
        
        if _identifier_re.match(name) is None:
            raise ValueError("Field name is not a valid identifier: {!r}".format(name))
        
        subform = Form(self.name + "." + name)
        
        f = {
            'field_type': 'object',
            'polymorphic': False,
            'name': name,
            'form': subform,
            'nullable': nullable,
            'multivalue': multivalue,
        }
        
        self.fields[name] = f
        self.order.append(name)
        return subform
        
    def add_polymorphic_object_field(
        self,
        name: str,
        type_choices: List[str],
        type_field: str = "type",
        default_type: Optional[str] = None,
        nullable: bool = False,
        multivalue: bool = False
    ):
        """
        Adds an object field that can change the type of object that is entered based on
        the answer to the first question (the 'type_field'). This field is automatically
        added to each returned subfield and is included in the returned data.
        
        Return a number of subforms corresponding to each of the type choices.
        """
        if name in self.fields:
            raise ValueError("Field named {!r} already exists in this form".format(name))
        
        if _identifier_re.match(name) is None:
            raise ValueError("Field name is not a valid identifier: {!r}".format(name))
        
        if _identifier_re.match(type_field) is None:
            raise ValueError("Type field name is not a valid identifier: {!r}".format(type_field))
            
        if default_type is not None and default_type not in type_choices:
            raise ValueError("Default type not in the listed choices: {!r}".format(default_type)) 
            
        if len(type_choices) < 2:
            raise ValueError("Polymorphic object field must use at least 2 different types")
            
        if len(set(type_choices)) != len(type_choices):
            raise ValueError("Every choice of type for polymorphic object must be unique")
            
        subforms = {}
        subforms_list = []
        dummy_first_form = None
        for ch in type_choices:
            if ch == "":
                raise ValueError("blank type choice not allowed. Use type default instead")
            form = Form(self.name + "." + name)
            form.add_choice_field(type_field, type_choices, default=default_type)
            subforms[ch] = form
            subforms_list.append(form)
            dummy_first_form = form
        
        f = {
            'field_type': 'object',
            'polymorphic': True,
            'name': name,
            'types': subforms,
            'form': dummy_first_form,
            'nullable': nullable,
            'multivalue': multivalue,
        }
        
        self.fields[name] = f
        self.order.append(name)
        
        return subforms_list
        
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
        
    def fill(self) -> Dict[str, Any]:
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
                    # if this is the last path component, directly assign it to cur.
                    
                    if field_name.startswith('['):
                        # it is actually an array digit OR the user has entered the sentinel value
                        if field_name == '[None]':  # TODO: this should probably be a module-level constant
                            # nothing to do, the user gave a sentinel not actual data
                            continue
                        array_index = int(field_name[1:-1])
                        while len(cur) < array_index:
                            cur.append(None)
                        if len(cur) == array_index:
                            cur.append(value)
                    else:
                        cur[field_name] = value
                else:
                    # otherwise, this path component specifies a dict or array to be added
                    if field_name.startswith('['):
                        # it is actually an array digit
                        array_index = int(field_name[1:-1])
                        while len(cur) < array_index + 1:
                            if path[idx + 1].startswith('['):
                                cur.append(list())
                            else:
                                cur.append(dict())
                        cur = cur[array_index]
                    else:
                        if field_name not in cur:
                            if path[idx + 1].startswith('['):
                                cur[field_name] = list()
                            else:
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
        self._multivalue_index = -1
        
        for fname in self.fields:
            f = self.fields[fname]
            if f['field_type'] == 'object':
                if f['polymorphic']:
                    for option in f['types']:
                        f['types'][option]._reset()
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
            if subform._has_more_prompts():
                return True
        
        # or if we are waiting for multivalue:
        if self._in_multivalue:
            return True
        
        return False
        
        
    def _ask(self, parents: List[str]) -> Tuple[List[str], Any]:
        """
        Ask the user to give data for a field. The user is prompted for the field
        that comes after the last one they were prompted for. If they haven't yet
        been prompted, the first field added to the form is used.
        
        :param parents: Parents of this field. Used for subform field identification.
        The top-level fields will have this be an empty list.
        :return: The full field path retrieved and the value that the user entered for it.
        If the user entered the sentinel while being prompted for a multi-valued item,
        the full field path with an index of [None] is returned.
        :raises ValueError: If neither index or field are set to valid values, or if
        neither are set and a previous call to ask() resulted in the last field being
        prompted for.
        """
        if len(self.order) < 1:
            raise ValueError("no fields to ask about")
            
        index = self._cursor
        
        # if cursor is currently pointing to a valid field,
        # check whether it is a subfield that has more questions
        # before incrementing
        if self._cursor > -1 and self._cursor < len(self.order):
            f = self.fields[self.order[self._cursor]]
            if f['field_type'] != 'object' or not f['form']._has_more_prompts():
                if not self._in_multivalue:
                    index += 1
        else:
            if not self._in_multivalue:
                index += 1
        
        if index >= len(self.order):
            raise ValueError("no more questions to ask about; reset the form first".format(index))
            
        f = self.fields[self.order[index]]
        self._cursor = index
        
        multivalue = f['multivalue']
        if multivalue:
            if not self._in_multivalue:
                # we are entering a multivalue field for the first time
                self._in_multivalue = True
                self._multivalue_index = -1
            if f['field_type'] != 'object' or f['form']._cursor == -1:
                self._multivalue_index += 1
        
        path_comps = list(parents + [f['name']])
        full_path = '.'.join(path_comps)
        
        if f['field_type'] == 'autouuid':
            value = str(uuid.uuid4())
            if multivalue:
                path_comps += ["[" + str(self._multivalue_index) + "]"]
                
            path = '.'.join(path_comps).replace('.[', '[')
                
            print("Auto-generated {:s}: {:s}".format(path, value))
                
            if f['entry_hook'] is not None:
                f['entry_hook'](value)
            
            return path_comps, value
            
        elif f['field_type'] == 'simple':
            print("-------------")
            sentinel = f['sentinel']
            got_valid = False
            default_value = f['default']
            if default_value is not None and callable(default_value):
                default_value = default_value()
            while not got_valid:
                if self._in_multivalue:
                    full_path += "[" + str(self._multivalue_index) + "]"
                
                prompt = full_path.replace('.[', '[')
                if default_value is not None:
                    prompt += " (default: {!r})".format(default_value)
  
                if f['nullable']:
                    prompt += "\n(Ctrl-D for explicit null)"
                    
                if multivalue:
                    prompt += "\n(type {!r} to end adding values)".format(sentinel)
                    
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
                    if f['nullable'] or default_value is not None:
                        value = default_value
                        got_valid = True
                        continue
                        
                if multivalue and str_input == sentinel:
                    self._in_multivalue = False
                    self._multivalue_index = -1
                    return list(path_comps + ["[None]"]), None
                
                try:
                    value = f['type'](str_input)
                    got_valid = True
                except ValueError as e:
                    print("Error: " + str(e))
                    
            if multivalue:
                path_comps += ["[" + str(self._multivalue_index) + "]"]
                
            if f['entry_hook'] is not None:
                f['entry_hook'](value)

            # we now have a valid task, have it set as default if that is what we do
            if f['default_last_entered']:
                f['default'] = value
            return path_comps, value
        elif f['field_type'] == 'object':
            subform = f['form']
            
            # first if we havent asked anyfin and we are on a multivalue, we need to ask if the list
            # ends here
            if multivalue and subform._cursor == -1:
                if not entry.confirm("{:s} is a list of values. Enter another one?".format(full_path.replace('.[', '['))):
                    # this is treated as hitting a sentinel
                    path_comps += ["[None]"]
                    self._in_multivalue = False
                    self._cursor += 1
                    return path_comps, None
            
            if multivalue:
                full_path += "[" + str(self._multivalue_index) + "]"
                path_comps += ["[" + str(self._multivalue_index) + "]"]
                
            # if we havent asked anyfin and the subform entirely is nullable, prompt
            # to see if the user even wants to do a value
            if f['nullable'] and subform._cursor == -1:
                if not entry.confirm("{:s} is nullable. Enter value for it?".format(full_path.replace('.[', '['))):
                    if self._in_multivalue:
                        subform._reset()
                    else:
                        subform._cursor_to_end()
                    
                    self._cursor += 1
                    return path_comps, None
                    
            comps, value = subform._ask(path_comps)
            # check if we just got the type for a polymorphic object
            if f['polymorphic'] and subform._cursor == 0:  # it is guaranteed to be the first question
                selected_subform = f['types'][value]
                selected_subform._reset()
                selected_subform._cursor = 0
                f['form'] = selected_subform
                if not selected_subform._has_more_prompts():
                    selected_subform._reset()
                
            if self._in_multivalue and not subform._has_more_prompts():
                subform._reset()
            return comps, value
        else:
            raise ValueError("unknown field_type: {!r}".format(f['field_type']))
            
    def _cursor_to_end(self):
        self._cursor = len(self) - 1
        
    def _cursor_to_start(self):
        self._cursor = -1
        
    def __len__(self) -> int:
        return len(self.fields)
        
        
        
