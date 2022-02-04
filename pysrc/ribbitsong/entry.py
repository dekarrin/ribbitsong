from typing import Optional, TypeVar, Callable

from .store import Model, FieldValue


_T = TypeVar('_T')


def get_row(model: Model, prompt: Optional[str] = None) -> dict[str, FieldValue]:
    if prompt is not None:
        print(prompt)
        
    row = {}
    for f in model:
        field = model[f]
        v = get(field.type, "{:s}:".format(field.name), allow_blank=True)
        row[field.name] = v
        
    return row
    

def pause(prompt: Optional[str] = None):
    if prompt is None:
        prompt = "(press enter)"
    else:
        prompt = prompt.rstrip() + " (press enter)"
        
    get(str, prompt, allow_blank=True)
    return
    
    
def confirm(prompt: Optional[str] = None) -> bool:
    if prompt is None:
        prompt = "(Y/N)"
    else:
        prompt = prompt.rstrip() + " (Y/N)"
    ch = get_choice(str.lower, "y", "n", "yes", "no", prompt=prompt)
    return ch == "y" or ch == "yes"
    
    
def get_choice(type_conv: Callable[[str], _T], *choices: list[_T], prompt: Optional[str] = None, allow_blank: bool = False) -> _T:
    """Prompt for choice until user enters valid one"""
    
    selected = None
    while selected is None:
        entered = get(type_conv, prompt, allow_blank)
        if entered in choices:
            selected = entered
    
    return selected
    

def get(type_conv: Callable[[str], _T], prompt: Optional[str] = None, allow_blank: bool = False) -> _T:
    """Prompt for type until user enters a valid one."""
    
    valid = None
    while valid is None:
        if prompt is not None:
            prompt = prompt.rstrip() + " "
            
        raw = input(prompt)
        try:
            valid = type_conv(raw)
            if isinstance(valid, str) and valid == "" and not allow_blank:
                valid = None
        except ValueError:
            pass
            
    return valid