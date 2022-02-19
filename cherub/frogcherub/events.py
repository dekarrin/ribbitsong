import uuid
from typing import Optional, Dict, List, Set


class ParadoxAddress:
    """
    The path within paradox space-time of someone or something. Includes the universe,
    the timeline, and the location.
    
    If coming as a result of a search operation, the indexes of each within their respective
    collection list is given as well. For instance, if a char was found in the third universe
    in an Event, the universe_index would be 2. And if they were found in the second timeline
    within that universe, the timeline_index would be 1, etc.
    
    For cases where indices are not provided, they all default to -1.
    """
    
    def __init__(self, **kwargs):
        self.universe = str(kwargs.get('universe', ''))
        self.timeline = str(kwargs.get('timeline', ''))
        self.location = str(kwargs.get('location', ''))
        self.universe_index = int(kwargs.get('universe_index', -1))
        self.timeline_index = int(kwargs.get('timeline_index', -1))
        self.location_index = int(kwargs.get('location_index', -1))
        
    def copy(self) -> 'ParadoxAddress':
        return ParadoxAddress(
            universe=self.universe,
            timeline=self.timeline,
            location=self.location,
            universe_index=self.universe_index,
            timeline_index=self.timeline_index,
            location_index=self.location_index
        )
        
    def __eq__(self, other) -> bool:
        if not isinstance(other, ParadoxAddress):
            return False
            
        self_tuple = (self.universe, self.timeline, self.location, self.universe_index, self.timeline_index, self.location_index)
        other_tuple = (other.universe, other.timeline, other.location, other.universe_index, other.timeline_index, other.location_index)
        return self_tuple == other_tuple
        
    def __hash__(self) -> int:
        return hash((self.universe, self.timeline, self.location, self.universe_index, self.timeline_index, self.location_index))
        
    def __str__(self) -> str:
        fmt = "<{:s}({:d}):{:s}({:d}):{:s}({:d})>"
        return fmt.format(self.universe, self.universe_index, self.timeline, self.timeline_index, self.location, self.location_index)

    def all_indices_equal(self, value) -> bool:
        return self.location_index == self.timeline_index == self.universe_index == value


class Citation:
    types = ['dialog', 'narration', 'media', 'commentary']

    # noinspection PyShadowingBuiltins
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

    def copy(self) -> 'Citation':
        """
        Return a deep copy of this Citation.
        """
        return Citation.from_dict(self.to_dict())
            
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
        self._paragraph = value
        
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

    # noinspection PyShadowingBuiltins
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
            self._citation = cit
                
        # dont raise value error because we are not covering narrative_immediate

    def copy(self) -> 'Constraint':
        """
        Return a deep copy of this Constraint.
        """
        return Constraint.from_dict(self.to_dict())
            
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
        
    @distance.setter
    def distance(self, value: str):
        if self.type != 'relative':
            raise NotImplementedError("{!r}-type constraints do not have a distance property".format(self.type))
        self._distance = value

    @staticmethod
    def from_dict(d: Dict) -> 'Constraint':
        t = d['type'].lower()
        return Constraint(t, **d)
        

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

    # noinspection PyShadowingBuiltins
    def __init__(self, type: str, **kwargs):
        type = type.lower()
        if type not in Tag.types:
            raise ValueError("invalid tag type; must be one of: {!r}".format(Tag.types))
            
        self._type = type
        self._actor = ""
        self._target = ""
        self._appearance = ""
        self._property = ""
        self._value = ""
        self._item = ""
        self._consumed = False
        self._opposite_port_event = ""
        self._location = ""
        self._source_items = []
        self._result_items = []
        self._results_in_sylladex = []
        
        if self.type == 'appearance_changed':
            if 'recipient' in kwargs:
                self._target = str(kwargs.get('recipient'))
            self._target = kwargs.get('target', self._target)
            self._appearance = kwargs.get('appearance', self._appearance)
        elif self.type == "state_changed":
            if 'recipient' in kwargs:
                self._target = str(kwargs.get('recipient'))
            self._target = kwargs.get('target', self._target)
            self._property = kwargs.get('property', self._property)
            self._value = kwargs.get('value', self._value)
        elif self.type == "char_obtains_item":
            if 'character' in kwargs:
                self._actor = str(kwargs.get('character'))
            self._actor = str(kwargs.get('actor', self._actor))
            self._item = kwargs.get('item', self._item)
        elif self.type == "char_drops_item":
            if 'character' in kwargs:
                self._actor = str(kwargs.get('character'))
            self._actor = str(kwargs.get('actor', self._actor))
            self._item = kwargs.get('item', self._item)
        elif self.type == "char_uses_item":
            if 'character' in kwargs:
                self._actor = str(kwargs.get('character'))
            self._actor = str(kwargs.get('actor', self._actor))
            self._item = kwargs.get('item', self._item)
            self._consumed = bool(kwargs.get('consumed', self._consumed))
        elif self.type == "char_gives_item_to_char":
            if 'giver' in kwargs:
                self._actor = str(kwargs.get('giver'))
            if 'receiver' in kwargs:
                self._target = str(kwargs.get('receiver'))
            self._actor = str(kwargs.get('actor', self._actor))
            self._target = str(kwargs.get('target', self._target))
            self._item = kwargs.get('item', self._item)
        elif self.type == "char_dies":
            if 'character' in kwargs:
                self._actor = str(kwargs.get('character'))
            self._actor = str(kwargs.get('actor', self._actor))
        elif self.type == "char_born":
            if 'character' in kwargs:
                self._actor = str(kwargs.get('character'))
            self._actor = str(kwargs.get('actor', self._actor))
        elif self.type == "char_resurrected":
            if 'character' in kwargs:
                self._actor = str(kwargs.get('character'))
            self._actor = str(kwargs.get('actor', self._actor))
        elif self.type == "char_ports_in":
            if 'character' in kwargs:
                self._actor = str(kwargs.get('character'))
            if 'port_out_event' in kwargs:
                self._opposite_port_event = str(kwargs.get('port_out_event'))
            self._actor = str(kwargs.get('actor', self._actor))
            self._opposite_port_event = str(kwargs.get('opposite_port_event', self._opposite_port_event))
        elif self.type == "char_ports_out":
            if 'character' in kwargs:
                self._actor = str(kwargs.get('character'))
            if 'port_in_event' in kwargs:
                self._opposite_port_event = str(kwargs.get('port_in_event'))
            self._actor = str(kwargs.get('actor', self._actor))
            self._opposite_port_event = kwargs.get('opposite_port_event', self._opposite_port_event)
        elif self.type == "char_enters_location":
            if 'character' in kwargs:
                self._actor = str(kwargs.get('character'))
            self._actor = str(kwargs.get('actor', self._actor))
            self._location = kwargs.get('location', self._location)
        elif self.type == "char_exits_location":
            if 'character' in kwargs:
                self._actor = str(kwargs.get('character'))
            self._actor = str(kwargs.get('actor', self._actor))
            self._location = kwargs.get('location', self._location)
        elif self.type == "char_falls_asleep":
            if 'character' in kwargs:
                self._actor = str(kwargs.get('character'))
            self._actor = str(kwargs.get('actor', self._actor))
        elif self.type == "char_wakes_up":
            if 'character' in kwargs:
                self._actor = str(kwargs.get('character'))
            self._actor = str(kwargs.get('actor', self._actor))
        elif self.type == "item_merged":
            if 'by' in kwargs:
                self._actor = str(kwargs.get('by'))
            self._actor = str(kwargs.get('actor', self._actor))
            self._source_items = list(kwargs.get('source_items', self._source_items))
            self._result_items = list(kwargs.get('result_items', self._result_items))
            self._results_in_sylladex = list(kwargs.get('results_in_sylladex', self._results_in_sylladex))
        elif self.type == "item_split":
            if 'by' in kwargs:
                self._actor = str(kwargs.get('by'))
            self._actor = str(kwargs.get('actor', self._actor))
            self._source_items = list(kwargs.get('source_items', self._source_items))
            self._result_items = list(kwargs.get('result_items', self._result_items))
            self._results_in_sylladex = list(kwargs.get('results_in_sylladex', self._results_in_sylladex))
        else:
            raise ValueError("should never happen")

    def copy(self) -> 'Tag':
        """
        Return a deep copy of this Tag.
        """
        return Tag.from_dict(self.to_dict())
            
    def __eq__(self, other) -> bool:
        if not isinstance(other, Tag):
            return False
        if other.type != self.type:
            return False

        if self.type == 'appearance_changed':
            if self.target != other.target:
                return False
            if self.appearance != other.appearance:
                return False
        elif self.type == "state_changed":
            if self.target != other.target:
                return False
            if self.property_name != other.property_name:
                return False
            if self.value != other.value:
                return False
        elif self.type == "char_obtains_item":
            if self.actor != other.actor:
                return False
            if self.item != other.item:
                return False
        elif self.type == "char_drops_item":
            if self.actor != other.actor:
                return False
            if self.item != other.item:
                return False
        elif self.type == "char_uses_item":
            if self.actor != other.actor:
                return False
            if self.item != other.item:
                return False
            if self.consumed != other.consumed:
                return False
        elif self.type == "char_gives_item_to_char":
            if self.actor != other.actor:
                return False
            if self.target != other.target:
                return False
            if self.item != other.item:
                return False
        elif self.type == "char_dies":
            if self.actor != other.actor:
                return False
        elif self.type == "char_born":
            if self.actor != other.actor:
                return False
        elif self.type == "char_resurrected":
            if self.actor != other.actor:
                return False
        elif self.type == "char_ports_in":
            if self.actor != other.actor:
                return False
            if self.opposite_port_event != other.opposite_port_event:
                return False
        elif self.type == "char_ports_out":
            if self.actor != other.actor:
                return False
            if self.opposite_port_event != other.opposite_port_event:
                return False
        elif self.type == "char_enters_location":
            if self.actor != other.actor:
                return False
            if self.location != other.location:
                return False
        elif self.type == "char_exits_location":
            if self.actor != other.actor:
                return False
            if self.location != other.location:
                return False
        elif self.type == "char_falls_asleep":
            if self.actor != other.actor:
                return False
        elif self.type == "char_wakes_up":
            if self.actor != other.actor:
                return False
        elif self.type == "item_merged":
            if self.source_items != other.source_items:
                return False
            if self.result_items != other.result_items:
                return False
            if self.results_in_sylladex != other.results_in_sylladex:
                return False
            if self.actor != other.actor:
                return False
        elif self.type == "item_split":
            if self.source_items != other.source_items:
                return False
            if self.result_items != other.result_items:
                return False
            if self.results_in_sylladex != other.results_in_sylladex:
                return False
            if self.actor != other.actor:
                return False
        else:
            raise ValueError("should never happen")
            
        return True
        
    def __hash__(self) -> int:
        if self.type == 'appearance_changed':
            return hash((self.type, self.target, self.appearance))
        elif self.type == "state_changed":
            return hash((self.type, self.target, self.property_name, self.value))
        elif self.type == "char_obtains_item":
            return hash((self.type, self.actor, self.item))
        elif self.type == "char_drops_item":
            return hash((self.type, self.actor, self.item))
        elif self.type == "char_uses_item":
            return hash((self.type, self.actor, self.item, self.consumed))
        elif self.type == "char_gives_item_to_char":
            return hash((self.type, self.actor, self.target, self.item))
        elif self.type == "char_dies":
            return hash((self.type, self.actor))
        elif self.type == "char_born":
            return hash((self.type, self.actor))
        elif self.type == "char_resurrected":
            return hash((self.type, self.actor))
        elif self.type == "char_ports_in":
            return hash((self.type, self.actor, self.opposite_port_event))
        elif self.type == "char_ports_out":
            return hash((self.type, self.actor, self.opposite_port_event))
        elif self.type == "char_enters_location":
            return hash((self.type, self.actor, self.location))
        elif self.type == "char_exits_location":
            return hash((self.type, self.actor, self.location))
        elif self.type == "char_falls_asleep":
            return hash((self.type, self.actor))
        elif self.type == "char_wakes_up":
            return hash((self.type, self.actor))
        elif self.type == "item_merged":
            return hash((self.type, self.source_items, self.result_items, self.results_in_sylladex, self.actor))
        elif self.type == "item_split":
            return hash((self.type, self.source_items, self.result_items, self.results_in_sylladex, self.actor))
        else:
            raise ValueError("should never happen")
            
    def __str__(self):
        s = "Tag<".format(self.type)
        if self.type == "appearance_changed":
            s += "APPEARANCE OF {:s} -> {:s}".format(self.target, self.appearance)
        elif self.type == "state_changed":
            s += "{:s}.{:s} = {!r}".format(self.target, self.property_name, self.value)
        elif self.type == "char_obtains_item":
            s += "{:s} GETS {:s}".format(self.actor, self.item)
        elif self.type == "char_drops_item":
            s += "{:s} DROPS {:s}".format(self.actor, self.item)
        elif self.type == "char_uses_item":
            s += "{:s} USES {:s}{:s}".format(self.actor, self.item, " UP" if self.consumed else "")
        elif self.type == "char_gives_item_to_char":
            s += "{:s} GIVES {:s} TO {:s}".format(self.actor, self.item, self.target)
        elif self.type == "char_dies":
            s += "{:s} DIES".format(self.actor)
        elif self.type == "char_born":
            s += "{:s} IS BORN".format(self.actor)
        elif self.type == "char_resurrected":
            s += "{:s} IS RESURRECTED".format(self.actor)
        elif self.type == "char_ports_in":
            port_mark = ""
            if self.opposite_port_event is not None and self.opposite_port_event != "":
                port_mark = "FROM {:s}".format(self.opposite_port_event)
            s += "{:s} PORTS IN{:s}".format(self.actor, port_mark)
        elif self.type == "char_ports_out":
            port_mark = ""
            if self.opposite_port_event is not None and self.opposite_port_event != "":
                port_mark = "TO {:s}".format(self.opposite_port_event)
            s += "{:s} PORTS OUT{:s}".format(self.actor, port_mark)
        elif self.type == "char_enters_location":
            loc_mark = " " + self.location if self.location is not None and self.location != "" else ""
            s += "{:s} ENTERS{:s}".format(self.actor, loc_mark)
        elif self.type == "char_exits_location":
            loc_mark = " " + self.location if self.location is not None and self.location != "" else ""
            s += "{:s} EXITS{:s}".format(self.actor, loc_mark)
        elif self.type == "char_falls_asleep":
            s += "{:s} FALLS ASLEEP".format(self.actor)
        elif self.type == "char_wakes_up":
            s += "{:s} WAKES UP".format(self.actor)
        elif self.type == "item_merged":
            source_mark = '[' + ','.join(self.source_items) + ']'
            results_mark = '[' + ','.join(self.result_items) + ']'
            sylladex_mark = '[' + ','.join(self.results_in_sylladex) + ']'

            fmt = "MERGE {:s} -> {:s} BY {!r}, SENDING {:s} TO INVENTORY"
            s += fmt.format(source_mark, results_mark, self.actor, sylladex_mark)
        elif self.type == "item_split":
            source_mark = '[' + ','.join(self.source_items) + ']'
            results_mark = '[' + ','.join(self.result_items) + ']'
            sylladex_mark = '[' + ','.join(self.results_in_sylladex) + ']'

            fmt = "SPLIT {:s} -> {:s} BY {!r}, SENDING {:s} TO INVENTORY"
            s += fmt.format(source_mark, results_mark, self.actor, sylladex_mark)
        else:
            raise ValueError("should never happen")
            
        s += ">"
        return s
        
    def to_dict(self) -> Dict:
        d = {'type': self.type}

        if self.type == 'appearance_changed':
            d['target'] = self.target
            d['appearance'] = self.appearance
        elif self.type == "state_changed":
            d['target'] = self.target
            d['property'] = self.property_name
            d['value'] = self.value
        elif self.type == "char_obtains_item":
            d['actor'] = self.actor
            d['item'] = self.item
        elif self.type == "char_drops_item":
            d['actor'] = self.actor
            d['item'] = self.item
        elif self.type == "char_uses_item":
            d['actor'] = self.actor
            d['item'] = self.item
            d['consumed'] = self.consumed
        elif self.type == "char_gives_item_to_char":
            d['actor'] = self.actor
            d['target'] = self.target
            d['item'] = self.item
        elif self.type == "char_dies":
            d['actor'] = self.actor
        elif self.type == "char_born":
            d['actor'] = self.actor
        elif self.type == "char_resurrected":
            d['actor'] = self.actor
        elif self.type == "char_ports_in":
            d['actor'] = self.actor
            d['opposite_port_event'] = self.opposite_port_event
        elif self.type == "char_ports_out":
            d['actor'] = self.actor
            d['opposite_port_event'] = self.opposite_port_event
        elif self.type == "char_enters_location":
            d['actor'] = self.actor
            d['location'] = self.location
        elif self.type == "char_exits_location":
            d['actor'] = self.actor
            d['location'] = self.location
        elif self.type == "char_falls_asleep":
            d['actor'] = self.actor
        elif self.type == "char_wakes_up":
            d['actor'] = self.actor
        elif self.type == "item_merged":
            d['actor'] = self.actor
            d['source_items'] = list(self.source_items)
            d['result_items'] = list(self.result_items)
            d['results_in_sylladex'] = list(self.results_in_sylladex)
        elif self.type == "item_split":
            d['actor'] = self.actor
            d['source_items'] = list(self.source_items)
            d['result_items'] = list(self.result_items)
            d['results_in_sylladex'] = list(self.results_in_sylladex)
        else:
            raise ValueError("should never happen")
            
        return d
            
    @property
    def type(self) -> str:
        return self._type

    @property
    def target(self) -> str:
        if self.type not in ['appearance_changed', 'state_changed', 'char_gives_item_to_char']:
            raise NotImplementedError("{!r}-type constraints do not have a target property".format(self.type))
        return self._target

    @target.setter
    def target(self, value: str):
        if self.type not in ['appearance_changed', 'state_changed', 'char_gives_item_to_char']:
            raise NotImplementedError("{!r}-type constraints do not have a target property".format(self.type))
        self._target = value

    @property
    def appearance(self) -> str:
        if self.type != 'appearance_changed':
            raise NotImplementedError("{!r}-type constraints do not have an appearance property".format(self.type))
        return self._appearance

    @appearance.setter
    def appearance(self, value: str):
        if self.type != 'appearance_changed':
            raise NotImplementedError("{!r}-type constraints do not have an appearance property".format(self.type))
        self._appearance = value

    @property
    def property_name(self) -> str:
        if self.type != 'state_changed':
            raise NotImplementedError("{!r}-type constraints do not have a property_name property".format(self.type))
        return self._property

    @property_name.setter
    def property_name(self, value: str):
        if self.type != 'state_changed':
            raise NotImplementedError("{!r}-type constraints do not have a property_name property".format(self.type))
        self._property = value

    @property
    def value(self) -> str:
        if self.type != 'state_changed':
            raise NotImplementedError("{!r}-type constraints do not have a value property".format(self.type))
        return self._value

    @value.setter
    def value(self, value: str):
        if self.type != 'state_changed':
            raise NotImplementedError("{!r}-type constraints do not have a value property".format(self.type))
        self._value = value

    @property
    def actor(self) -> str:
        if self.type not in [
            'char_obtains_item',
            'char_drops_item',
            'char_uses_item',
            'char_gives_item_to_char',
            'char_dies',
            'char_born',
            'char_resurrected',
            'char_ports_in',
            'char_ports_out',
            'char_enters_location',
            'char_exits_location',
            'char_falls_asleep',
            'char_wakes_up',
            'item_split',
            'item_merged'
        ]:
            raise NotImplementedError("{!r}-type constraints do not have an 'actor' property".format(self.type))
        return self._actor

    @actor.setter
    def actor(self, value: str):
        if self.type not in [
            'char_obtains_item',
            'char_drops_item',
            'char_uses_item',
            'char_gives_item_to_char',
            'char_dies',
            'char_born',
            'char_resurrected',
            'char_ports_in',
            'char_ports_out',
            'char_enters_location',
            'char_exits_location',
            'char_falls_asleep',
            'char_wakes_up',
            'item_split',
            'item_merged',
        ]:
            raise NotImplementedError("{!r}-type constraints do not have an 'actor' property".format(self.type))
        self._actor = value

    @property
    def item(self) -> str:
        if self.type not in ['char_obtains_item', 'char_drops_item', 'char_uses_item', 'char_gives_item_to_char']:
            raise NotImplementedError("{!r}-type constraints do not have an item property".format(self.type))
        return self._item

    @item.setter
    def item(self, value: str):
        if self.type not in ['char_obtains_item', 'char_drops_item', 'char_uses_item', 'char_gives_item_to_char']:
            raise NotImplementedError("{!r}-type constraints do not have an item property".format(self.type))
        self._item = value

    @property
    def consumed(self) -> bool:
        if self.type != 'char_uses_item':
            raise NotImplementedError("{!r}-type constraints do not have a consumed property".format(self.type))
        return self._consumed

    @consumed.setter
    def consumed(self, value: bool):
        if self.type != 'char_uses_item':
            raise NotImplementedError("{!r}-type constraints do not have a consumed property".format(self.type))
        self._consumed = value

    @property
    def opposite_port_event(self) -> str:
        if self.type not in ['char_ports_in', 'char_ports_out']:
            raise NotImplementedError("{!r}-type constraints do not have an opposite_port_event property".format(self.type))
        return self._opposite_port_event

    @opposite_port_event.setter
    def opposite_port_event(self, value: str):
        if self.type not in ['char_ports_in', 'char_ports_out']:
            raise NotImplementedError("{!r}-type constraints do not have an opposite_port_event property".format(self.type))
        self._opposite_port_event = value

    @property
    def location(self) -> str:
        if self.type not in ['char_exits_location', 'char_enters_location']:
            raise NotImplementedError("{!r}-type constraints do not have a location property".format(self.type))
        return self._location

    @location.setter
    def location(self, value: str):
        if self.type not in ['char_exits_location', 'char_enters_location']:
            raise NotImplementedError("{!r}-type constraints do not have a location property".format(self.type))
        self._location = value

    @property
    def source_items(self) -> List[str]:
        if self.type not in ['item_split', 'item_merged']:
            raise NotImplementedError("{!r}-type constraints do not have a source_items property".format(self.type))
        return self._source_items

    @source_items.setter
    def source_items(self, value: List[str]):
        if self.type not in ['item_split', 'item_merged']:
            raise NotImplementedError("{!r}-type constraints do not have a source_items property".format(self.type))
        self._source_items = value

    @property
    def result_items(self) -> List[str]:
        if self.type not in ['item_split', 'item_merged']:
            raise NotImplementedError("{!r}-type constraints do not have a result_items property".format(self.type))
        return self._result_items

    @result_items.setter
    def result_items(self, value: List[str]):
        if self.type not in ['item_split', 'item_merged']:
            raise NotImplementedError("{!r}-type constraints do not have a result_items property".format(self.type))
        self._result_items = value

    @property
    def results_in_sylladex(self) -> List[str]:
        if self.type not in ['item_split', 'item_merged']:
            msg = "{!r}-type constraints do not have a results_in_sylladex property"
            raise NotImplementedError(msg.format(self.type))
        return self._results_in_sylladex

    @results_in_sylladex.setter
    def results_in_sylladex(self, value: List[str]):
        if self.type not in ['item_split', 'item_merged']:
            msg = "{!r}-type constraints do not have a results_in_sylladex property"
            raise NotImplementedError(msg.format(self.type))
        self._results_in_sylladex = value

    @staticmethod
    def from_dict(d: Dict) -> 'Tag':
        t = d['type'].lower()
        return Tag(t, **d)


class Location:
    """
    Represents a location and the items and characters it has in it at a particular moment of the narrative.
    """
    def __init__(self, **kwargs):
        self.path = kwargs.get('path', "")
        self.characters = list(kwargs.get('characters', list()))
        self.items = list(kwargs.get('items', list()))

    def copy(self) -> 'Location':
        return Location(path=self.path, items=self.items, characters=self.characters)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Location):
            return False
        if self.path != other.path:
            return False
        if self.items != other.items:
            return False
        if self.characters != other.characters:
            return False
        return True

    def __hash__(self) -> int:
        return hash((self.path, self.items, self.characters))

    def __str__(self) -> str:
        chars_mark = '[' + ','.join(self.characters) + ']'
        items_mark = '[' + ','.join(self.items) + ']'
        s = "<{:s}: chars={:s}, items={:s}>".format(self.path, chars_mark, items_mark)
        return s

    def to_dict(self) -> Dict:
        d = {
            'path': self.path,
            'characters': self.characters,
            'items': self.items
        }
        return d

    @staticmethod
    def from_dict(d: Dict) -> 'Location':
        return Location(**d)


class Timeline:
    """
    Represents all relevant locations within a timeline at a particular moment of the narrative.
    """
    def __init__(self, **kwargs):
        self.path = kwargs.get('path', "")
        self.locations: List[Location] = list()

        locs = list(kwargs.get('locations', list()))
        for loc in locs:
            if isinstance(loc, dict):
                loc = Location.from_dict(loc)
            self.locations.append(loc)

    def copy(self) -> 'Timeline':
        return Timeline(path=self.path, locations=self.locations)
        
    def get_location(self, location: str, index: int = -1) -> Optional[Location]:
        """
        Get a Location in this Timeline by name (path).

        If index is provided it is used instead of timeline.
        """
        if index >= 0:
            if index >= len(self.locations):
                return None
            else:
                return self.locations[index]
        else:
            for loc in self.locations:
                if loc.path == location:
                    return loc
            return None

    def __eq__(self, other) -> bool:
        if not isinstance(other, Timeline):
            return False
        if self.path != other.path:
            return False
        if self.locations != other.locations:
            return False
        return True

    def __hash__(self) -> int:
        return hash((self.path, self.locations))

    def __str__(self) -> str:
        return "<{:s}: locations={:s}>".format(self.path, str(self.locations))

    def to_dict(self) -> Dict:
        d = {
            'path': self.path,
            'locations': [loc.to_dict() for loc in self.locations]
        }

        return d

    @staticmethod
    def from_dict(d: Dict) -> 'Timeline':
        return Timeline(**d)


class Universe:
    """
    Represents all relevant timelines within a universe at a particular moment of the narrative.
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', "")
        self.timelines: List[Timeline] = list()

        tls = list(kwargs.get("timelines", list()))
        for tl in tls:
            if isinstance(tl, dict):
                tl = Timeline.from_dict(tl)
            self.timelines.append(tl)

    def copy(self) -> 'Universe':
        return Universe(name=self.name, timelines=self.timelines)
        
    def get_timeline(self, timeline: str, index: int = -1) -> Optional[Timeline]:
        """
        Get a Timeline in this universe by name (path).

        If index is provided it is used instead of timeline.
        """
        if index >= 0:
            if index >= len(self.timelines):
                return None
            else:
                return self.timelines[index]
        else:
            for tl in self.timelines:
                if tl.path == timeline:
                    return tl
            return None

    def __eq__(self, other) -> bool:
        if not isinstance(other, Universe):
            return False
        if self.name != other.name:
            return False
        if self.timelines != other.timelines:
            return False
        return True

    def __hash__(self) -> int:
        return hash((self.name, self.timelines))

    def __str__(self) -> str:
        return "<{:s}: timelines={:s}>".format(self.name, str(self.timelines))

    def to_dict(self) -> Dict:
        d = {
            'name': self.name,
            'timelines': [tl.to_dict() for tl in self.timelines]
        }

        return d

    @staticmethod
    def from_dict(d: Dict) -> 'Universe':
        return Universe(**d)


class Event:
    def __init__(self, **kwargs):
        self.id = str(kwargs.get('id', uuid.uuid4()))
        self.name = str(kwargs.get('name', ""))
        self.description = str(kwargs.get('description', ""))
        self.portrayed_in: Optional[Citation] = None
        self.citations: List[Citation] = list()
        self.constraints: List[Constraint] = list()
        self.tags: List[Tag] = list()
        self.universes: List[Universe] = list()
        self.meta: Set[str] = set(kwargs.get('meta', list()))

        portrayed_in = kwargs.get('portrayed_in', self.portrayed_in)
        if isinstance(portrayed_in, dict):
            portrayed_in = Citation.from_dict(portrayed_in)
        self.portrayed_in = portrayed_in

        citations = list(kwargs.get('citations', self.citations))
        for cit in citations:
            if isinstance(cit, dict):
                cit = Citation.from_dict(cit)
            self.citations.append(cit)

        constraints = list(kwargs.get('constraints', self.constraints))
        for con in constraints:
            if isinstance(con, dict):
                con = Constraint.from_dict(con)
            self.constraints.append(con)

        tags = list(kwargs.get('tags', self.tags))
        for t in tags:
            if isinstance(t, dict):
                t = Tag.from_dict(t)
            self.tags.append(t)

        univs = list(kwargs.get('universes', self.universes))
        for u in univs:
            if isinstance(u, dict):
                u = Universe.from_dict(u)
            self.universes.append(u)
            
    def scene_at_end(
        self,
        location: Optional[str] = None,
        timeline: Optional[str] = None,
        universe: Optional[str] = None,
    ) -> Location:
        """
        Give what the requested location looks like as a result of playing
        back all event tags present on this event.
        
        :param location: The path of the location to get. If none given, the first one in the selected timeline is used.
        :param timeline: The path of the timeline to get. If none given, the first one in the selected universe is used.
        :param universe: The name of the universe to get. If none given, the first one is used.
        :return: A Location that contains the items and characters that remain after all
        event tags have run.
        """
        univ_idx = 0
        if universe is not None:
            found = False
            for idx, univ in enumerate(self.universes):
                if univ.name == universe:
                    univ_idx = idx
                    found = True
                    break
            if not found:
                raise ValueError("event does not occur in universe with name {!r}".format(universe))
        target_univ = self.universes[univ_idx]
                
        tl_idx = 0
        if timeline is not None:
            found = False
            for idx, tl in enumerate(target_univ.timelines):
                if tl.path == timeline:
                    tl_idx = idx
                    found = True
                    break
            if not found:
                raise ValueError("event does not occur in timeline with name {!r}".format(timeline))
        target_tl = target_univ.timelines[tl_idx]
        
        loc_idx = 0
        if location is not None:
            found = False
            for idx, loc in enumerate(target_tl.locations):
                if loc.path == location:
                    loc_idx = idx
                    found = True
            if not found:
                raise ValueError("event does not occur in location with name {!r}".format(location))
        target_loc = target_tl.locations[loc_idx]
        
        end_items = set(target_loc.items)
        end_chars = set(target_loc.characters)
        for t in self.tags:
            if t.type == "char_obtains_item":
                if t.actor in end_chars:
                    end_items.remove(t.item)
            elif t.type == "char_drops_item":
                if t.actor in end_chars:
                    end_items.add(t.item)
            elif t.type == "char_uses_item":
                if t.actor in end_chars and t.consumed:
                    end_items.remove(t.item)
            elif t.type == "char_ports_in":
                if t.actor not in end_chars:
                    end_chars.add(t.actor)
            elif t.type == "char_ports_out":
                if t.actor in end_chars:
                    end_chars.remove(t.actor)
            elif t.type == "char_enters_location":
                if t.actor not in end_chars:
                    end_chars.add(t.actor)
            elif t.type == "char_exits_location":
                if t.actor in end_chars:
                    end_chars.remove(t.actor)
            elif t.type == "item_merged" or t.type == "items_split":
                if t.actor is None or t.actor in end_chars:
                    for r in end_items:
                        if r in t.source_items:
                            end_items.remove(r)
                    for r in t.result_items:
                        if r not in t.results_in_sylladex:
                            end_items.add(r)
        
        end_location = Location(path=target_loc.path, items=list(end_items), characters=list(end_chars))
        return end_location
        
    def all_addresses(self) -> List[ParadoxAddress]:
        """Get all paradox addresses currently present in this event."""
        
        addresses = list()
        
        for u_idx, u in enumerate(self.universes):
            for tl_idx, tl in enumerate(u.timelines):
                for loc_idx, loc in enumerate(tl.locations):
                    addr = ParadoxAddress(universe=u.name, timeline=tl.path, location=loc.path)
                    addr.universe_index = u_idx
                    addr.timeline_index = tl_idx
                    addr.location_index = loc_idx
                    addresses.append(addr)
        
        return addresses
        
    def address_of(self, item_or_char: str) -> Optional[ParadoxAddress]:
        """
        Find the location of the given item
        """
        
        address = None
        for u_idx, u in enumerate(self.universes):
            for tl_idx, tl in enumerate(u.timelines):
                for loc_idx, loc in enumerate(tl.locations):
                    if item_or_char in loc.characters or item_or_char in loc.items:
                        address = ParadoxAddress(location=loc.path, timeline=tl.path, universe=u.name)
                        address.location_index = loc_idx
                        address.timeline_index = tl_idx
                        address.universe_index = u_idx
                        break
                if address is not None:
                    break
            if address is not None:
                break
                
        return address
        
    def get_universe(self, address: ParadoxAddress) -> Optional[Universe]:
        """
        Get a Universe by name. Return None if not found.
        
        :param address: Must contain the universe to get. If universe_index is present, that will be used regardless
        of the value of its universe field.
        """

        if address.universe_index >= 0:
            if address.universe_index >= len(self.universes):
                return None
            else:
                return self.universes[address.universe_index]
        else:
            for u in self.universes:
                if u.name == address.universe:
                    return u
            return None
        
    def get_timeline(self, address: ParadoxAddress) -> Optional[Timeline]:
        """
        Get a Timeline by address. Return None if not found.
        
        :param address: Must contain the timeline to get and the universe it is located in. If indices are present,
        those will be used regardless of the value of their related name-based fields.
        """
        univ = self.get_universe(address)
        if univ is None:
            return None
        return univ.get_timeline(address.timeline, address.timeline_index)
        
    def get_location(self, address: ParadoxAddress) -> Optional[Location]:
        """
        Get a Location by address. Return None if not found.
        
        :param address: Must contain universe, timeline, and location names. If indices are present,
        those will be used regardless of the value of their related name-based fields.
        """
        tl = self.get_timeline(address)
        if tl is None:
            return None
        return tl.get_location(address.location, address.location_index)

    def copy(self) -> 'Event':
        return Event.from_dict(self.to_dict())

    def __eq__(self, other) -> bool:
        if not isinstance(other, Event):
            return False
        if self.id != other.id:
            return False
        if self.name != other.name:
            return False
        if self.description != other.description:
            return False
        if self.portrayed_in != other.portrayed_in:
            return False
        if self.citations != other.citations:
            return False
        if self.constraints != other.constraints:
            return False
        if self.tags != other.tags:
            return False
        if self.universes != other.universes:
            return False
        return True

    def __hash__(self) -> int:
        return hash((self.id, self.name, self.description, self.portrayed_in, self.citations, self.constraints, self.tags, self.universes))

    def __str__(self) -> str:
        return "Event<{:s} {!r}>".format(self.id, self.name)

    def to_dict(self) -> Dict:
        d = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'portrayed_in': self.portrayed_in.to_dict() if self.portrayed_in is not None else None,
            'citations': [c.to_dict() for c in self.citations],
            'constraints': [c.to_dict() for c in self.constraints],
            'tags': [t.to_dict() for t in self.tags],
            'universes': [u.to_dict() for u in self.universes]
        }

        return d

    @staticmethod
    def from_dict(d: Dict) -> 'Event':
        return Event(**d)
