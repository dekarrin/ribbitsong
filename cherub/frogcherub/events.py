import uuid
from typing import Optional

class Citation:
    types = ['dialog', 'narration', 'media', 'commentary']

    def __init__(self, type: str, **kwargs):
        type = type.lower()
        if type not in Citation.types:
            raise ValueError("invalid citation type; must be one of: {!r}".format(Citation.types))
            
        self._type = type
        self._work = kwargs.get('work', 'homestuck')
        self._panel = 0
        self._line = 0
        self._character = ""
        self._paragraph = 0
        self._sentence = 0
        self._timestamp = ""
        self._volume = 0
        self._page = 0
        
        if self.type == "dialog":
            self._panel = int(kwargs.get('panel', self._panel))
            self._line = int(kwargs.get('line', self._line))
            self._character = kwargs.get('character', self._character)
        elif self.type == "narration":
            self._panel = int(kwargs.get('panel', self._panel))
            self._paragraph = int(kwargs.get('paragraph', self._paragraph))
            self._sentence = int(kwargs.get('sentence', self._sentence))
        elif self.type == "media":
            self._panel = int(kwargs.get('panel', self._panel))
            self._timestamp = kwargs.get('timestamp', self._timestamp)
        elif self.type == "commentary":
            self._volume = int(kwargs.get('volume', self._volume))
            self._page = int(kwargs.get('page', self._page))
        else:
            raise ValueError("should never happen")
            
    def __eq__(self, other) -> bool:
        if not isinstance(other, Citation):
            return False
        if other.type != self.type:
            return False
            
        if self.type == 'dialog':
            if self.panel != other.panel:
                return False
            if self.line != other.line:
                return False
            if self.character != other.character:
                return False
        elif self.type == 'narration':
            if self.panel != other.panel:
                return False
            if self.paragraph != other.paragraph:
                return False
            if self.sentence != other.sentence:
                return False
        elif self.type == 'media':
            if self.panel != other.panel:
                return False
            if self.timestamp != other.timestamp:
                return False
        elif self.type == 'commentary':
            if self.volume != other.volume:
                return False
            if self.page != other.page:
                return False
        else:
            raise ValueError("should never happen")
            
        return True
        
    def __hash__(self) -> int:
        if self.type == 'dialog':
            return hash((self.type, self.panel, self.line, self.character))
        elif self.type == 'narration':
            return hash((self.type, self.panel, self.paragraph, self.sentence))
        elif self.type == 'media':
            return hash((self.type, self.panel, self.timestamp))
        elif self.type == 'commentary':
            return hash((self.type, self.volume, self.page))
        else:
            raise ValueError("should never happen")
            
    def __str__(self):
        s = "Citation<{:s} ".format(self.type)
        if self.type == "dialog":
            s += "P{:d}, Line {:d}, by '{:s}'".format(self.panel, self.line, self.character)
        elif self.type == "narration":
            s += "P{:d}-PA{:d}-S{:d}".format(self.panel, self.paragraph, self.sentence)
        elif self.type == "media":
            s += "P{:d}@{:s}".format(self.panel, self.timestamp)
        elif self.type == "commentary":
            s += "v{:d}p{:d}".format(self.volume, self.page)
        else:
            raise ValueError("should never happen")
            
        s += ">"
        return s
        
    def to_dict(self) -> Dict:
        d = {'type': self.type}
        
        if self.type == "dialog":
            d['panel'] = self.panel
            d['line'] = self.line
            d['character'] = self.character
        elif self.type == "narration":
            d['panel'] = self.panel
            d['paragraph'] = self.paragraph
            d['sentence'] = self.sentence
        elif self.type == "media":
            d['panel'] = self.panel
            d['timestamp'] = self.timestamp
        elif self.type == "commentary":
            d['volume'] = self.volume
            d['page'] = self.page
        else:
            raise ValueError("should never happen")
            
        return d
            
    @property
    def type(self) -> str:
        return self._type
        
    @property
    def work(self) -> str:
        return self._work
        
    @work.setter
    def work(self, value: str):
        self._work = value
        
    @property
    def panel(self) -> int:
        if self.type not in ['dialog', 'narration', 'media']:
            raise NotImplementedError("{!r}-type citations do not have a panel property".format(self.type))
        return self._panel
        
    @panel.setter
    def panel(self, value: int):
        if self.type not in ['dialog', 'narration', 'media']:
            raise NotImplementedError("{!r}-type citations do not have a panel property".format(self.type))
        self._panel = value
        
    @property
    def line(self) -> int:
        if self.type != "dialog":
            raise NotImplementedError("{!r}-type citations do not have a line property".format(self.type))
        return self._line
        
    @line.setter
    def line(self, value: int):
        if self.type != "dialog":
            raise NotImplementedError("{!r}-type citations do not have a line property".format(self.type))
        self._line = value
        
    @property
    def character(self) -> str:
        if self.type != 'dialog':
            raise NotImplementedError("{!r}-type citations do not have a character property".format(self.type))
        return self._character
        
    @character.setter
    def character(self, value: str):
        if self.type != 'dialog':
            raise NotImplementedError("{!r}-type citations do not have a character property".format(self.type))
        self._character = value
        
    @property
    def paragraph(self) -> int:
        if self.type != "narration":
            raise NotImplementedError("{!r}-type citations do not have a paragraph property".format(self.type))
        return self._paragraph
        
    @paragraph.setter
    def paragraph(self, value: int):
        if self.type != "narration":
            raise NotImplementedError("{!r}-type citations do not have a paragraph property".format(self.type))
        self._paragraph = paragraph
        
    @property
    def sentence(self) -> int:
        if self.type != 'narration':
            raise NotImplementedError("{!r}-type citations do not have a sentence property".format(self.type))
        return self._sentence
        
    @sentence.setter
    def sentence(self, value: int):
        if self.type != 'dialog':
            raise NotImplementedError("{!r}-type citations do not have a sentence property".format(self.type))
        self._sentence = value
        
    @property
    def timestamp(self) -> str:
        if self.type != 'media':
            raise NotImplementedError("{!r}-type citations do not have a timestamp property".format(self.type))
        return self._timestamp
        
    @timestamp.setter
    def timestamp(self, value: str):
        if self.type != 'media':
            raise NotImplementedError("{!r}-type citations do not have a timestamp property".format(self.type))
        self._timestamp = value
        
    @property
    def volume(self) -> int:
        if self.type != "commentary":
            raise NotImplementedError("{!r}-type citations do not have a volume property".format(self.type))
        return self._volume
        
    @volume.setter
    def volume(self, value: int):
        if self.type != "commentary":
            raise NotImplementedError("{!r}-type citations do not have a volume property".format(self.type))
        self._volume = value
        
    @property
    def page(self) -> int:
        if self.type != 'commentary':
            raise NotImplementedError("{!r}-type citations do not have a page property".format(self.type))
        return self._page
        
    @page.setter
    def page(self, value: int):
        if self.type != 'commentary':
            raise NotImplementedError("{!r}-type citations do not have a page property".format(self.type))
        self._page = value
        
    @staticmethod
    def from_dict(d: Dict) -> 'Citation':
        t = d['type'].lower()
        return Citation(t, **d)


class Constraint:
    types = [
        'narrative_entrypoint',
        'narrative_jump',
        'narrative_causal',
        'narrative_immediate'
        'absolute',
        'relative',
        'causal',
        'sync'
    ]

    def __init__(self, type: str, **kwargs):
        type = type.lower()
        if type not in Constraint.types:
            raise ValueError("invalid constraint type; must be one of: {!r}".format(Constraint.types))
            
        self._type = type
        self._ref_event = ""
        self._is_after = True
        self._distance = ""
        self._time = ""
        self._citation = None
        
        if self.type in ["narrative_immediate", "narrative_causal", "narrative_jump"]:
            self._ref_event = kwargs.get('ref_event', self._ref_event)
            self._is_after = bool(kwargs.get('is_after', self._is_after))
        elif self.type == "absolute":
            self._time = kwargs.get('time', self._time)
            
            cit = kwargs.get('citation', self._citation)
            if isinstance(cit, dict):
                cit = Citation.from_dict(cit)
            self._citation = cit
        elif self.type == "relative":
            self._ref_event = kwargs.get('ref_event', self._ref_event)
            self._is_after = bool(kwargs.get('is_after', self._is_after))
            self._distance = kwargs.get('distance', self._distance)
            
            cit = kwargs.get('citation', self._citation)
            if isinstance(cit, dict):
                cit = Citation.from_dict(cit)
            self._citation = cit
        elif self.type == "causal":
            self._ref_event = kwargs.get('ref_event', self._ref_event)
            self._is_after = bool(kwargs.get('is_after', self._is_after))
            
            cit = kwargs.get('citation', self._citation)
            if isinstance(cit, dict):
                cit = Citation.from_dict(cit)
            self._citation = cit
        elif self.type == "sync":
            self._ref_event = kwargs.get('ref_event', self._ref_event)
            
            cit = kwargs.get('citation', self._citation)
            if isinstance(cit, dict):
                cit = Citation.from_dict(cit)
                
        # dont raise value error because we are not covering narrative_immediate
            
    def __eq__(self, other) -> bool:
        if not isinstance(other, Constraint):
            return False
        if other.type != self.type:
            return False
            
        if self.type == 'narrative_entrypoint':
            pass  # nothing else to check
        elif self.type == 'narrative_jump':
            if self.ref_event != other.ref_event:
                return False
            if self.is_after != other.is_after:
                return False
        elif self.type == 'narrative_causal':
            if self.ref_event != other.ref_event:
                return False
            if self.is_after != other.is_after:
                return False
        elif self.type == 'narrative_immediate':
            if self.ref_event != other.ref_event:
                return False
            if self.is_after != other.is_after:
                return False
        elif self.type == 'absolute':
            if self.time != other.time:
                return False
            if self.citation != other.citation:
                return False
        elif self.type == 'relative':
            if self.ref_event != other.ref_event:
                return False
            if self.is_after != other.is_after:
                return False
            if self.distance != other.distance:
                return False
            if self.citation != other.citation:
                return False
        elif self.type == 'causal':
            if self.ref_event != other.ref_event:
                return False
            if self.is_after != other.is_after:
                return False
            if self.citation != other.citation:
                return False
        elif self.type == 'sync':
            if self.ref_event != other.ref_event:
                return False
            if self.citation != other.citation:
                return False
        else:
            raise ValueError("should never happen")
            
        return True
        
    def __hash__(self) -> int:
        if self.type == 'narrative_entrypoint':
            return hash((self.type,))
        if self.type == 'narrative_immediate':
            return hash((self.type, self.ref_event, self.is_after))
        elif self.type == 'narrative_jump':
            return hash((self.type, self.ref_event, self.is_after))
        elif self.type == 'narrative_causal':
            return hash((self.type, self.ref_event, self.is_after))
        elif self.type == 'absolute':
            return hash((self.type, self.time, hash(self.citation)))
        elif self.type == 'relative':
            return hash((self.type, self.ref_event, self.is_after, self.distance, hash(self.citation)))
        elif self.type == 'causal':
            return hash((self.type, self.ref_event, self.is_after, hash(self.citation)))
        elif self.type == 'sync':
            return hash((self.type, self.ref_event, hash(self.citation)))
        else:
            raise ValueError("should never happen")
            
    def __str__(self):
        s = "Constraint<{:s} ".format(self.type)
        if self.type == "narrative_entrypoint":
            pass  # nothing further to add
        elif self.type == "narrative_immediate":
            s += "{:s}{:s}".format('+' if self.is_after else '-', self.ref_event)
        elif self.type == "narrative_jump":
            s += "{:s}{:s}".format('+' if self.is_after else '-', self.ref_event)
        elif self.type == "narrative_causal":
            s += "{:s}{:s}".format('+' if self.is_after else '-', self.ref_event)
        elif self.type == "absolute":
            s += "@{:s} ({:s}cited)".format(self.time, "" if self.citation is not None else "not ")
        elif self.type == "relative":
            after_mark = '+' if self.is_after else '-'
            cite_mark = "" if self.citation is not None else "not "
            s += "{:s}{:s} by {:s} ({:s}cited)".format(after_mark, self.ref_event, self.distance, cite_mark)
        elif self.type == "causal":
            after_mark = '+' if self.is_after else '-'
            cite_mark = "" if self.citation is not None else "not "
            s += "{:s}{:s} ({:s}cited)".format(after_mark, self.ref_event, cite_mark)
        elif self.type == "sync":
            cite_mark = "" if self.citation is not None else "not "
            s += "WITH {:s} ({:s}cited)".format(self.ref_event, cite_mark)
        else:
            raise ValueError("should never happen")
            
        s += ">"
        return s
        
    def to_dict(self) -> Dict:
        d = {'type': self.type}
        
        if self.type == "narrative_entrypoint":
            pass  # nothing further to add
        elif self.type in ["narrative_immediate", "narrative_jump", "narrative_causal"]:
            d['ref_event'] = self.ref_event
            d['is_after'] = self.is_after
        elif self.type == "absolute":
            d['time'] = self.time
            d['citation'] = None if self.citation is None else self.citation.to_dict()
        elif self.type == "relative":
            d['ref_event'] = self.ref_event
            d['is_after'] = self.is_after
            d['distance'] = self.distance
            d['citation'] = None if self.citation is None else self.citation.to_dict()
        elif self.type == "causal":
            d['ref_event'] = self.ref_event
            d['is_after'] = self.is_after
            d['citation'] = None if self.citation is None else self.citation.to_dict()
        elif self.type == "sync":
            d['ref_event'] = self.ref_event
            d['citation'] = None if self.citation is None else self.citation.to_dict()
        else:
            raise ValueError("should never happen")
            
        return d
            
    @property
    def type(self) -> str:
        return self._type
        
    @property
    def ref_event(self) -> str:
        if self.type not in ['narrative_immediate', 'narrative_jump', 'narrative_causal', 'relative', 'causal', 'sync']:
            raise NotImplementedError("{!r}-type constraints do not have a ref_event property".format(self.type))
        return self._ref_event
        
    @ref_event.setter
    def ref_event(self, value: str):
        if self.type not in ['narrative_immediate', 'narrative_jump', 'narrative_causal', 'relative', 'causal', 'sync']:
            raise NotImplementedError("{!r}-type constraints do not have a ref_event property".format(self.type))
        self._ref_event = value
        
    @property
    def is_after(self) -> bool:
        if self.type not in ['narrative_immediate', 'narrative_jump', 'narrative_causal', 'relative', 'causal']:
            raise NotImplementedError("{!r}-type constraints do not have an is_after property".format(self.type))
        return self._is_after
        
    @is_after.setter
    def is_after(self, value: bool):
        if self.type not in ['narrative_immediate', 'narrative_jump', 'narrative_causal', 'relative', 'causal']:
            raise NotImplementedError("{!r}-type constraints do not have an is_after property".format(self.type))
        self._is_after = value
        
    @property
    def citation(self) -> Optional[Citation]:
        if self.type not in ['absolute', 'relative', 'causal', 'sync']:
            raise NotImplementedError("{!r}-type constraints do not have a citation property".format(self.type))
        return self._citation
        
    @citation.setter
    def citation(self, value: Optional[Citation]):
        if self.type not in ['absolute', 'relative', 'causal', 'sync']:
            raise NotImplementedError("{!r}-type constraints do not have a citation property".format(self.type))
        self._citation = value
        
    @property
    def time(self) -> str:
        if self.type != 'absolute':
            raise NotImplementedError("{!r}-type constraints do not have a time property".format(self.type))
        return self._time
        
    @time.setter
    def time(self, value: str):
        if self.type != 'absolute':
            raise NotImplementedError("{!r}-type constraints do not have a time property".format(self.type))
        self._time = value
        
    @property
    def distance(self) -> str:
        if self.type != 'relative':
            raise NotImplementedError("{!r}-type constraints do not have a distance property".format(self.type))
        return self._distance
        
    @ditance.setter
    def distance(self, value: str):
        if self.type != 'relative':
            raise NotImplementedError("{!r}-type constraints do not have a distance property".format(self.type))
        self._distance = value
        

class Tag:
    types = [
        "appearance_changed",
        "state_changed",
        "char_obtains_item",
        "char_drops_item",
        "char_uses_item",
        "char_gives_item_to_char",
        "char_dies",
        "char_born",
        "char_resurrected",
        "char_ports_in",
        "char_ports_out",
        "char_enters_location",
        "char_exits_location",
        "char_falls_asleep",
        "char_wakes_up",
        "item_merged",
        "item_split"
    ]

    def __init__(self, type: str, **kwargs):
        type = type.lower()
        if type not in Tag.types:
            raise ValueError("invalid tag type; must be one of: {!r}".format(Tag.types))
            
        self._type = type
        self._recipient = ""
        self._appearance = ""
        self._property = ""
        self._value = ""
        self._character = ""  # TODO: merge with 'actor'
        self._item = ""
        self._consumed = False
        self._giver = ""  # TODO: merge with 'actor'
        self._receiver = ""  # TODO: merge with recipient
        self._port_in_event  # TODO: merge with 'opposite_port_event'
        self._port_out_event  # TODO: merge with 'opposite_port_event'
        self._location = ""
        self._source_items = []
        self._result_items = []
        self._by = ""  # TODO: merge with 'actor'
        self._results_in_sylladex = []
        
        if self.type == 'appearance_changed':
            self._recipient = kwargs.get('recipient', self._recipient)
            self._appearance = kwargs.get('appearance', self._appearance)
        elif self.type == "state_changed":
            self._recipient = kwargs.get('recipient', self._recipient)
            self._property = kwargs.get('property', self._property)
            self._value = kwargs.get('value', self._value)
        elif self.type == "char_obtains_item":
            self._character = kwargs.get('character', self._character)
            self._item = kwargs.get('item', self._item)
        elif self.type == "char_drops_item":
            self._character = kwargs.get('character', self._character)
            self._item = kwargs.get('item', self._item)
        elif self.type == "char_uses_item":
            self._character = kwargs.get('character', self._character)
            self._item = kwargs.get('item', self._item)
            self._consumed = bool(kwargs.get('consumed', self._consumed))
        elif self.type == "char_gives_item_to_char":
            self._giver = kwargs.get('giver', self._giver)
            self._receiver = bool(kwargs.get('receiver', self._receiver))
            self._item = kwargs.get('item', self._item)
        elif self.type == "char_dies":
            self._character = kwargs.get('character', self._character)
        elif self.type == "char_born":
            self._character = kwargs.get('character', self._character)
        elif self.type == "char_resurrected":
            self._character = kwargs.get('character', self._character)
        elif self.type == "char_ports_in":
            self._character = kwargs.get('character', self._character)
            self._port_out_event = kwargs.get('port_out_event', self._port_out_event)
        elif self.type == "char_ports_out":
            self._character = kwargs.get('character', self._character)
            self._port_in_event = kwargs.get('port_in_event', self._port_in_event)
        elif self.type == "char_enters_location":
            self._character = kwargs.get('character', self._character)
            self._location = kwargs.get('location', self._location)
        elif self.type == "char_exits_location":
            self._character = kwargs.get('character', self._character)
            self._location = kwargs.get('location', self._location)
        elif self.type == "char_falls_asleep":
            self._character = kwargs.get('character', self._character)
        elif self.type == "char_wakes_up":
            self._character = kwargs.get('character', self._character)
        elif self.type == "item_merged":
            self._source_items = list(kwargs.get('source_items', self._source_items))
            self._result_items = list(kwargs.get('result_items', self._result_items))
            self._by = kwargs.get('by', self._by)
            self._results_in_sylladex = list(kwargs.get('results_in_sylladex', self._results_in_sylladex))
        elif self.type == "item_split":
            self._source_items = list(kwargs.get('source_items', self._source_items))
            self._result_items = list(kwargs.get('result_items', self._result_items))
            self._by = kwargs.get('by', self._by)
            self._results_in_sylladex = list(kwargs.get('results_in_sylladex', self._results_in_sylladex))
        else:
            raise ValueError("should never happen")
            
    def __eq__(self, other) -> bool:
        if not isinstance(other, Constraint):
            return False
        if other.type != self.type:
            return False
            
        if self.type == 'narrative_entrypoint':
            pass  # nothing else to check
        elif self.type == 'narrative_jump':
            if self.ref_event != other.ref_event:
                return False
            if self.is_after != other.is_after:
                return False
        elif self.type == 'narrative_causal':
            if self.ref_event != other.ref_event:
                return False
            if self.is_after != other.is_after:
                return False
        elif self.type == 'narrative_immediate':
            if self.ref_event != other.ref_event:
                return False
            if self.is_after != other.is_after:
                return False
        elif self.type == 'absolute':
            if self.time != other.time:
                return False
            if self.citation != other.citation:
                return False
        elif self.type == 'relative':
            if self.ref_event != other.ref_event:
                return False
            if self.is_after != other.is_after:
                return False
            if self.distance != other.distance:
                return False
            if self.citation != other.citation:
                return False
        elif self.type == 'causal':
            if self.ref_event != other.ref_event:
                return False
            if self.is_after != other.is_after:
                return False
            if self.citation != other.citation:
                return False
        elif self.type == 'sync':
            if self.ref_event != other.ref_event:
                return False
            if self.citation != other.citation:
                return False
        else:
            raise ValueError("should never happen")
            
        return True
        
    def __hash__(self) -> int:
        if self.type == 'narrative_entrypoint':
            return hash((self.type,))
        if self.type == 'narrative_immediate':
            return hash((self.type, self.ref_event, self.is_after))
        elif self.type == 'narrative_jump':
            return hash((self.type, self.ref_event, self.is_after))
        elif self.type == 'narrative_causal':
            return hash((self.type, self.ref_event, self.is_after))
        elif self.type == 'absolute':
            return hash((self.type, self.time, hash(self.citation)))
        elif self.type == 'relative':
            return hash((self.type, self.ref_event, self.is_after, self.distance, hash(self.citation)))
        elif self.type == 'causal':
            return hash((self.type, self.ref_event, self.is_after, hash(self.citation)))
        elif self.type == 'sync':
            return hash((self.type, self.ref_event, hash(self.citation)))
        else:
            raise ValueError("should never happen")
            
    def __str__(self):
        s = "Constraint<{:s} ".format(self.type)
        if self.type == "narrative_entrypoint":
            pass  # nothing further to add
        elif self.type == "narrative_immediate":
            s += "{:s}{:s}".format('+' if self.is_after else '-', self.ref_event)
        elif self.type == "narrative_jump":
            s += "{:s}{:s}".format('+' if self.is_after else '-', self.ref_event)
        elif self.type == "narrative_causal":
            s += "{:s}{:s}".format('+' if self.is_after else '-', self.ref_event)
        elif self.type == "absolute":
            s += "@{:s} ({:s}cited)".format(self.time, "" if self.citation is not None else "not ")
        elif self.type == "relative":
            after_mark = '+' if self.is_after else '-'
            cite_mark = "" if self.citation is not None else "not "
            s += "{:s}{:s} by {:s} ({:s}cited)".format(after_mark, self.ref_event, self.distance, cite_mark)
        elif self.type == "causal":
            after_mark = '+' if self.is_after else '-'
            cite_mark = "" if self.citation is not None else "not "
            s += "{:s}{:s} ({:s}cited)".format(after_mark, self.ref_event, cite_mark)
        elif self.type == "sync":
            cite_mark = "" if self.citation is not None else "not "
            s += "WITH {:s} ({:s}cited)".format(self.ref_event, cite_mark)
        else:
            raise ValueError("should never happen")
            
        s += ">"
        return s
        
    def to_dict(self) -> Dict:
        d = {'type': self.type}
        
        if self.type == "narrative_entrypoint":
            pass  # nothing further to add
        elif self.type in ["narrative_immediate", "narrative_jump", "narrative_causal"]:
            d['ref_event'] = self.ref_event
            d['is_after'] = self.is_after
        elif self.type == "absolute":
            d['time'] = self.time
            d['citation'] = None if self.citation is None else self.citation.to_dict()
        elif self.type == "relative":
            d['ref_event'] = self.ref_event
            d['is_after'] = self.is_after
            d['distance'] = self.distance
            d['citation'] = None if self.citation is None else self.citation.to_dict()
        elif self.type == "causal":
            d['ref_event'] = self.ref_event
            d['is_after'] = self.is_after
            d['citation'] = None if self.citation is None else self.citation.to_dict()
        elif self.type == "sync":
            d['ref_event'] = self.ref_event
            d['citation'] = None if self.citation is None else self.citation.to_dict()
        else:
            raise ValueError("should never happen")
            
        return d
            
    @property
    def type(self) -> str:
        return self._type
        
    @property
    def ref_event(self) -> str:
        if self.type not in ['narrative_immediate', 'narrative_jump', 'narrative_causal', 'relative', 'causal', 'sync']:
            raise NotImplementedError("{!r}-type constraints do not have a ref_event property".format(self.type))
        return self._ref_event
        
    @ref_event.setter
    def ref_event(self, value: str):
        if self.type not in ['narrative_immediate', 'narrative_jump', 'narrative_causal', 'relative', 'causal', 'sync']:
            raise NotImplementedError("{!r}-type constraints do not have a ref_event property".format(self.type))
        self._ref_event = value
        
    @property
    def is_after(self) -> bool:
        if self.type not in ['narrative_immediate', 'narrative_jump', 'narrative_causal', 'relative', 'causal']:
            raise NotImplementedError("{!r}-type constraints do not have an is_after property".format(self.type))
        return self._is_after
        
    @is_after.setter
    def is_after(self, value: bool):
        if self.type not in ['narrative_immediate', 'narrative_jump', 'narrative_causal', 'relative', 'causal']:
            raise NotImplementedError("{!r}-type constraints do not have an is_after property".format(self.type))
        self._is_after = value
        
    @property
    def citation(self) -> Optional[Citation]:
        if self.type not in ['absolute', 'relative', 'causal', 'sync']:
            raise NotImplementedError("{!r}-type constraints do not have a citation property".format(self.type))
        return self._citation
        
    @citation.setter
    def citation(self, value: Optional[Citation]):
        if self.type not in ['absolute', 'relative', 'causal', 'sync']:
            raise NotImplementedError("{!r}-type constraints do not have a citation property".format(self.type))
        self._citation = value
        
    @property
    def time(self) -> str:
        if self.type != 'absolute':
            raise NotImplementedError("{!r}-type constraints do not have a time property".format(self.type))
        return self._time
        
    @time.setter
    def time(self, value: str):
        if self.type != 'absolute':
            raise NotImplementedError("{!r}-type constraints do not have a time property".format(self.type))
        self._time = value
        
    @property
    def distance(self) -> str:
        if self.type != 'relative':
            raise NotImplementedError("{!r}-type constraints do not have a distance property".format(self.type))
        return self._distance
        
    @ditance.setter
    def distance(self, value: str):
        if self.type != 'relative':
            raise NotImplementedError("{!r}-type constraints do not have a distance property".format(self.type))
        self._distance = value

class Event:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', uuid.uuid4())
        self.name = kwargs.get('name', "")
        self.description = kwargs.get('description', "")
        