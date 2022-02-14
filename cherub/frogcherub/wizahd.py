import uuid

class Wizahd:
    def __init__(self, events):
        self._cursor = -1
        self._events = []
        
        self._universe = ""
        self._timeline = ""
        self._location = ""
        self._items = []
        self._chars = []
        
        self._comic_page = 0
        self._work = "homestuck"
        self._narrative_link = "causal"
        self._following = None
        
    def go_into_location(self, new_loc: str, to_panel=0):
        if self._following is None:
            raise ValueError("Not following any char yet")
        
        self.advance_narrative(to_panel)
        self.add_char_exit()
        self.advance_narrative(to_panel)
        self.scene_change(new_location)
        self.add_char_enter()            
        
    def add_char_exit(self, from_loc=None, char=None):
        if from_loc is None:
            from_loc = self._location
            
        if char is None:
            if self._following is None:
                raise ValueError("No char specified but not following any char either")
            char = self._following
        
        self._events[_self._cursor]['tags'].append({
            "type": "char_exits_location",
            "character": char,
            "location": from_loc
        })
        
    def add_char_enter(self, to_loc=None, char=None):
        if to_loc is None:
            to_loc = self._location
            
        if char is None:
            if self._following is None:
                raise ValueError("No char specified but not following any char either")
            char = self._following
        
        self._events[_self._cursor]['tags'].append({
            "type": "char_enters_location",
            "character": char,
            "location": to_loc
        })
        
    def get_last_event(self, location=None, timeline=None, univ=None) -> Tuple[Dict, Dict]:
        """
        Get the last entered event that occured at the given locality in paradox space.
        
        Return the event that occured there as well as a dict containing the location info.
        These will be None if the locality has not yet been visited.
        """
        if location is None:
            location = self._location
        if timeline is None:
            timeline = self._timeline
        if univ is None:
            univ = self._universe
            
        found_event = None
        found_locinfo = None
        for evt in reversed(self._events):
            for univ in evt['universes']:
                if univ['name'] == univ:
                    for tl in univ['timelines']:
                        if tl['path'] == timeline:
                            for loc in tl['locations']:
                                if loc['path'] == location:
                                    found_event = evt
                                    found_locinfo = loc
                                    break
                            if found_event is not None:
                                break
                    if found_event is not None:
                        break
            if found_event is not None:
                break
        
        return found_event, found_locinfo
        
    def scene_change(self, new_location, new_timeline=None, new_universe=None):
        if new_timeline is not None:
            dest_timeline = new_timeline
        else:
            dest_timeline = self._timeline
            
        if new_universe is not None:
            dest_universe = new_universe
        else:
            dest_universe = self._universe
        
        self._items = list()
        self._chars = list()
        
        evt, locinfo = self.get_last_event(new_location, dest_timeline, dest_universe)
        if locinfo is not None:
            items, characters = do_item_playback
        
        
        self._location = new_location
        self._events[_self._cursor]['universes'][0]['timelines'][0]['locations'][0]['path'] = new_location
        
        if new_timeline is not None:
            self._timeline = new_timeline
            self._events[_self._cursor]['universes'][0]['timelines'][0]['path'] = new_timeline
            
        if new_universe is not None:
            self._universe = new_universe
            self._events[_self._cursor]['universes'][0]['name'] = new_universe
        
    def next(self):
        self.goto(self._cursor + 1)
        
    def prev(self):
        self.goto(self._cursor - 1)
        
    def goto(self, cursor: int):
        if cursor < 0:
            raise ValueError("cursor needs to be > 0")
        if cursor >= len(self._events):
            raise ValueError("cursor bigger than number of events")
            
        self._cursor = cursor
        
        event = self._events[self._cursor]
        
        self._work = event['portrayed_in']['work']
        self._comic_page = event['portrayed_in']['panel']
        self._universe = event['universes'][0]['name']
        self._timeline = event['universes'][0]['timelines'][0]['path']
        self._location = event['universes'][0]['timelines'][0]['locations'][0]['path']
        self._items = event['universes'][0]['timelines'][0]['locations'][0]['items']
        self._chars = event['universes'][0]['timelines'][0]['locations'][0]['characters']
        
    def advance_narrative(self, to_panel=0):
        if self._comic_page > to_panel:
            raise ValueError("advance needs to happen after the current for a narrative")
            
        if to_panel > 0 and self._comic_page + 1 != to_panel:
            self._comic_page = to_panel
            self._narrative_link = "causal"
        else:
            self._comic_page += 1
            self._narrative_link = "immediate"
    
        self._cursor = len(self._events)
        self._events.append({
            'id': str(uuid.uuid4()),
            'name': "",
            'description': "",
            'portrayed_in': {
                "type": "narration",
                "work": self._work,
                "panel": self._comic_page,
                "paragraph": 0,
                "sentence": 0
            },
            'citations': [],
            'tags': [],
            'constraints': [
                {
                    "type": "narrative_" + self._narrative_link,
                    "ref_event": self._events[self._cursor - 1] if self._cursor >= 1 else None,
                    "is_after": True
                }
            ],
            'universes': [
                {
                    'name': self._universe,
                    'timelines': [
                        {
                            'path': self._timeline,
                            'locations': [
                                {
                                    'path': self._location,
                                    "characters": list(self._chars),
                                    "items": list(self._items)
                                }
                            ]
                        }
                    ]
                }
            ]
        })
        
    @property
    def following(self) -> str:
        return self._following
        
    @following.setter
    def following(self, value: str):
        self._following = value
        
    @property
    def id(self) -> str:
        return self._events[self._cursor]['id']
        
    @property
    def name(self) -> str:
        return self._events[self._cursor]['name']
        
    @name.setter
    def name(self, value: str):
        self._events[self._cursor]['name'] = value
        
    @property
    def description(self) -> str:
        return self._events[self._cursor]['description']
        
    @description.setter
    def description(self, value: str):
        self._events[self._cursor]['description'] = value
        
    @property
    def work(self) -> str:
        return self._work
        
    @work.setter
    def work(self, value: str):
        self._work = value
        self._events[self._cursor]['portrayed_in']['work'] = value
        
    @property
    def universe(self) -> str:
        return self._universe
        
    @universe.setter
    def universe(self, value: str):
        self._universe = value
        self._events[self._cursor]['universes'][0]['name'] = value
        
    @property
    def timeline(self) -> str:
        return self._timeline
        
    @timeline.setter
    def timeline(self, value: str):
        self._timeline = value
        self._events[self._cursor]['universes'][0]['timelines'][0]['path'] = value
        
    @property
    def location(self) -> str:
        return self._location
        
    @location.setter
    def location(self, value: str):
        self._location = value
        self._events[self._cursor]['universes'][0]['locations'][0]['path'] = value
        
    @property
    def comic_page(self) -> int:
        return self._comic_page
        
    @comic_page.setter
    def comic_page(self, value: int):
        self._comic_page = value
        self._events[self._cursor]['portrayed_in']['panel'] = value
    
    @property
    def items(self) -> list[str]:
        return list(self._items)
        
    @property
    def characters(self) -> list[str]:
        return list(self._chars)