
class SequenceProvider:
    """
    Returns elements in the sequence, one at a time. Each call to a SequenceProvider returns the
    next item in the sequence.
    
    Once the end of the members is reached, the next call returns the first element and
    the sequence repeats. To disable this, set repeat to False. In that case, calling
    after reaching the end returns None.
    
    If no members are provided at construction, calling the SequenceProvider will
    always return None.
    """
    
    def __init__(self, *members):
        self.members = list(members)
        self.repeat = True
        self._cursor = 0
        
    def __call__(self, *args):
        if self._cursor >= len(self.members):
            return None
            
        item = self.members[self._cursor]
        self._cursor += 1
        if self._cursor >= len(self.members) and self.repeat:
            self._cursor = 0
            
        return item
