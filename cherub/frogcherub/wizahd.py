from .events import Event, Tag, Citation, Constraint, Universe, Timeline, Location, ParadoxAddress

from .format import pretty_sequence
from typing import List, Optional


class Wizahd:
    def __init__(self, events: List[Event]):
        self.updated = False
    
        self._cursor = -1
        self._events = list(events)
        
        self._universe = ""
        self._timeline = ""
        self._location = ""
        self._items = set()
        self._chars = set()
        
        self._comic_page = 0
        self._work = "homestuck"
        self._narrative_link = "causal"
        self._following = None

        self._convo_participants = dict()
        
        if len(self._events) < 1:
            p = Citation("narration", work=self._work, panel=self._comic_page)
            c = Constraint("narrative_entrypoint")
            new_event = Event(portrayed_in=p, constraints=[c])
            self._events.append(new_event)

        self.goto(len(self._events) - 1)

    def pretty_str(self, tabs=0) -> str:
        leading = '  ' * tabs
        s = 'Wizahd<\n'
        s += leading + '  updated: {:s}'.format(str(self.updated)) + '\n'
        s += leading + '  _cursor: {:d}'.format(self._cursor) + '\n'
        s += leading + '  _universe: {:s}'.format(str(self._universe)) + '\n'
        s += leading + '  _timeline: {:s}'.format(str(self._timeline)) + '\n'
        s += leading + '  _location: {:s}'.format(str(self._location)) + '\n'
        s += pretty_sequence('_items', self._items, tabs+1) + '\n'
        s += pretty_sequence('_chars', self._chars, tabs+1) + '\n'
        s += leading + '  _comic_page: {:d}'.format(self._comic_page) + '\n'
        s += leading + '  _work: {:s}'.format(str(self._work)) + '\n'
        s += leading + '  _narrative_link: {:s}'.format(str(self._narrative_link)) + '\n'
        s += leading + '  _following: {:s}'.format(str(self._following)) + '\n'
        s += leading + '  _convo_participants: {:s}'.format(str(self._convo_participants)) + '\n'
        s += leading + '  current_event: {:s}'.format(self.current_event.pretty_str(tabs+1)) + '\n'
        s += leading + ">"
        return s

    def obtain_item(self, item: str, char: Optional[str] = None):
        if self._following is None and char is None:
            raise ValueError("Not following any char yet")
        if char is None:
            char = self._following

        char_addr = self.current_event.address_of(char)
        if char_addr is None:
            msg = "character {!r} is not yet in this event. Add them manually or give an entrance event"
            raise ValueError(msg.format(char))

        char_loc = self.current_event.get_location(char_addr)
        if item not in char_loc.items:
            msg = "item {!r} is not yet in this event in the same place as {!r}."
            msg += "Add it manually or give an event that adds one."
            raise ValueError(msg.format(item, char))

        self.add_char_item_interaction("char_obtains_item", char, item)

        char_loc.items.remove(item)
        if char_addr.all_indices_equal(0):
            self._items.remove(item)
            
        self.updated = True

    def drop_item(self, item: str, char: Optional[str] = None):
        if self._following is None and char is None:
            raise ValueError("Not following any char yet")
        if char is None:
            char = self._following

        char_addr = self.current_event.address_of(char)
        if char_addr is None:
            msg = "character {!r} is not yet in this event. Add them manually or give an entrance event"
            raise ValueError(msg.format(char))

        char_loc = self.current_event.get_location(char_addr)
        if item in char_loc.items:
            msg = "item {!r} is already in this event in the same place as {!r}."
            msg += "Remove it manually or give an event that removes one."
            raise ValueError(msg.format(item, char))

        self.add_char_item_interaction("char_drops_item", char, item)

        char_loc.items.add(item)
        if char_addr.all_indices_equal(0):
            self._items.add(item)
            
        self.updated = True

    def use_item(self, item: str, consumed: bool, char: Optional[str] = None):
        if self._following is None and char is None:
            raise ValueError("Not following any char yet")
        if char is None:
            char = self._following

        char_addr = self.current_event.address_of(char)
        if char_addr is None:
            msg = "character {!r} is not yet in this event. Add them manually or give an entrance event"
            raise ValueError(msg.format(char))

        char_loc = self.current_event.get_location(char_addr)

        self.add_char_item_interaction("char_uses_item", char, item, consumed=consumed)

        if consumed and item in char_loc.items:
            char_loc.items.remove(item)
            if char_addr.all_indices_equal(0):
                self._items.remove(item)
            
        self.updated = True

    def give_item(self, item: str, to_char: str, char: Optional[str] = None):
        if self._following is None and char is None:
            raise ValueError("Not following any char yet")
        if char is None:
            char = self._following

        char_addr = self.current_event.address_of(char)
        if char_addr is None:
            msg = "character {!r} is not yet in this event. Add them manually or give an entrance event"
            raise ValueError(msg.format(char))

        to_char_addr = self.current_event.address_of(to_char)
        if to_char_addr is None:
            msg = "character {!r} is not yet in this event. Add them manually or give an entrance event"
            raise ValueError(msg.format(to_char))

        self.add_char_item_interaction("char_gives_item_to_char", char, item, target=to_char)

        char_loc = self.current_event.get_location(char_addr)
        if item in char_loc.items:
            char_loc.items.remove(item)
            if char_addr.all_indices_equal(0):
                self._items.remove(item)
            
        self.updated = True

    def merge_items(self, items: List[str], results: List[str], sylladex_results: List[str], char: Optional[str] = None):
        if self._following is None and char is None:
            raise ValueError("Not following any char yet")
        if char is None:
            char = self._following

        char_addr = self.current_event.address_of(char)
        if char_addr is None:
            msg = "character {!r} is not yet in this event. Add them manually or give an entrance event"
            raise ValueError(msg.format(char))

        char_loc = self.current_event.get_location(char_addr)
        for item in items:
            if item not in char_loc.items:
                pass  # dont disallow this, the char may be using items in inventory and we arent yet tracking inventory
                      # so no way to check atm
        for result in results:
            if result in char_loc.items and result not in sylladex_results:
                msg = "result item {!r} is already in this event in the same place as {!r}."
                msg += "Remove it manually or give an event that removes it."
                raise ValueError(msg.format(result, char))

        self.add_char_item_interaction("item_merged", char, source_items=items, result_items=results, sylladex_results=sylladex_results)

        for item in items:
            if item in char_loc.items:
                char_loc.items.remove(item)
                if char_addr.all_indices_equal(0):
                    self._items.remove(item)
        for result in results:
            if result not in char_loc.items and result not in sylladex_results:
                char_loc.items.add(result)
                if char_addr.all_indices_equal(0):
                    self._items.add(result)
            
        self.updated = True

    def split_items(self, items: List[str], results: List[str], sylladex_results: List[str], char: Optional[str] = None):
        if self._following is None and char is None:
            raise ValueError("Not following any char yet")
        if char is None:
            char = self._following

        char_addr = self.current_event.address_of(char)
        if char_addr is None:
            msg = "character {!r} is not yet in this event. Add them manually or give an entrance event"
            raise ValueError(msg.format(char))

        char_loc = self.current_event.get_location(char_addr)
        for item in items:
            if item not in char_loc.items:
                pass  # dont disallow this, the char may be using items in inventory and we arent yet tracking inventory
                      # so no way to check atm
        for result in results:
            if result in char_loc.items and result not in sylladex_results:
                msg = "result item {!r} is already in this event in the same place as {!r}."
                msg += "Remove it manually or give an event that removes it."
                raise ValueError(msg.format(result, char))

        self.add_char_item_interaction("item_split", char, source_items=items, result_items=results, sylladex_results=sylladex_results)

        for item in items:
            if item in char_loc.items:
                char_loc.items.remove(item)
                if char_addr.all_indices_equal(0):
                    self._items.remove(item)
        for result in results:
            if result not in char_loc.items and result not in sylladex_results:
                char_loc.items.add(result)
                if char_addr.all_indices_equal(0):
                    self._items.add(result)
            
        self.updated = True

    def mc_start_convo(
        self,
        other_char: str,
        other_char_addr: Optional[ParadoxAddress] = None,
        to_panel=0
    ):
        if self._following is None:
            raise ValueError("Not following any char yet")

        self._convo_participants = {}
        self.advance_narrative(to_panel, for_dialog=True)
        self.current_event.portrayed_in = Citation('dialog', work=self._work, panel=self._comic_page)
        self.current_event.meta.add('convo')
        address = self.current_event.address_of(self._following)
        if address is None:
            raise ValueError("Followed char {!r} not present in current event. This should never happen.".format(self._following))
        self.mc_add_convo_participant(self._following, address=address)
        
        if other_char_addr is None:
            other_char_addr = address
        if other_char_addr.location == "":
            other_char_addr.location = self._location
        if other_char_addr.timeline == "":
            other_char_addr.timeline = self._timeline
        if other_char_addr.universe == "":
            other_char_addr.universe = self._universe
            
        self.mc_add_convo_participant(other_char, other_char_addr)
            
        self.updated = True

    def mc_continue_convo(self, to_panel=0):
        if self._following is None:
            raise ValueError("Not following any char yet")

        if "convo" not in self.current_event.meta:
            raise ValueError("Not yet in convo")

        self.advance_narrative(to_panel, for_dialog=True)
        self.current_event.meta.add('convo')

        for participant in self._convo_participants:
            addr = self._convo_participants[participant]
            self.mc_add_convo_participant(participant, addr)
            
        self.updated = True

    def mc_end_convo(self, to_panel=0):
        if self._following is None:
            raise ValueError("Not following any char yet")

        if "convo" not in self.current_event.meta:
            raise ValueError("Not yet in convo")

        self.advance_narrative(to_panel)
            
        self.updated = True
            
    def mc_add_convo_participant(self, char: str, address: ParadoxAddress):
        if "convo" not in self.current_event.meta:
            raise ValueError("Can't add a participant, not yet in convo")

        if char not in self._convo_participants:
            self._convo_participants[char] = address
        
        loc = self.current_event.get_location(address)
        if loc is None:
            loc = Location(path=address.location)
            tl = self.current_event.get_timeline(address)
            if tl is None:
                tl = Timeline(path=address.timeline)
                univ = self.current_event.get_universe(address)
                if univ is None:
                    univ = Universe(name=address.universe)
                    self.current_event.universes.append(univ)
                univ.timelines.append(tl)
            tl.locations.append(loc)
        
        if char not in loc.characters:
            loc.characters.add(char)

        self.current_event.meta.add('convo:' + str(char))
            
        self.updated = True
        
    def mc_go_into_location(self, new_loc: str, to_panel=0):
        if self._following is None:
            raise ValueError("Not following any char yet")
        
        self.advance_narrative(to_panel)
        self.add_char_exit()
        self.advance_narrative(to_panel)
        self.scene_change(new_loc)
        self.add_char_enter()
            
        self.updated = True

    def add_char_item_interaction(
            self,
            interaction_type: str,
            actor: str, item: str = "",
            target: str = "",
            consumed: bool = False,
            source_items: List[str] = None,
            result_items: List[str] = None,
            sylladex_results: List[str] = None
    ):
        if interaction_type not in ["char_obtains_item", "char_drops_item", "char_uses_item", "char_gives_item_to_char", "item_merged", "item_split"]:
            raise ValueError("not a valid item interaction type: {!r}".format(interaction_type))

        if source_items is None:
            source_items = list()
        if result_items is None:
            result_items = list()
        if sylladex_results is None:
            sylladex_results = list()

        tag_args = {
            "actor": actor,
        }

        if interaction_type in ['char_obtains_item', 'char_drops_item', 'char_uses_item', 'char_gives_item_to_char']:
            tag_args['item'] = item
        elif interaction_type in ['item_split', 'item_merged']:
            tag_args['source_items'] = list(source_items)
            tag_args['result_items'] = list(result_items)
            tag_args['results_in_sylladex'] = list(sylladex_results)

        if interaction_type == "char_uses_item":
            tag_args['consumed'] = consumed
        elif interaction_type == "char_gives_item_to_char":
            tag_args['target'] = target

        t = Tag(interaction_type, **tag_args)
        self.current_event.tags.append(t)
            
        self.updated = True

    def add_char_exit(self, from_loc=None, char=None):
        if from_loc is None:
            from_loc = self._location
            
        if char is None:
            if self._following is None:
                raise ValueError("No char specified but not following any char either")
            char = self._following
        
        exit_tag = Tag("char_exits_location", character=char, location=from_loc)
        self.current_event.tags.append(exit_tag)
            
        self.updated = True
        
    def add_char_enter(self, to_loc=None, char=None):
        if to_loc is None:
            to_loc = self._location
            
        if char is None:
            if self._following is None:
                raise ValueError("No char specified but not following any char either")
            char = self._following
        
        enter_tag = Tag("char_enters_location", character=char, location=to_loc)
        self.current_event.tags.append(enter_tag)
            
        self.updated = True

    def add_item(self, item: str):
        """
        Manually add an item to this event.

        :param item: The item to add.
        """
        if self._universe is None or self._timeline is None or self._location is None:
            raise ValueError("Need to follow UTL before adding item")

        if item in self._items:
            return
        self._items.add(item)
        self.current_event.universes[0].timelines[0].locations[0].items.add(item)

    def add_char(self, char: str):
        """
        Manually add a character to this event.

        :param char: The char to add.
        """
        if self._universe is None or self._timeline is None or self._location is None:
            raise ValueError("Need to follow UTL before adding char")

        if char in self._chars:
            return
        self._chars.add(char)
        self.current_event.universes[0].timelines[0].locations[0].characters.add(char)

    def remove_item(self, item: str):
        """
        Manually remove an item from this event.

        :param item: The item to remove.
        """
        if self._universe is None or self._timeline is None or self._location is None:
            raise ValueError("Need to follow UTL before removing item")

        if item not in self._items:
            return
        self._items.remove(item)
        self.current_event.universes[0].timelines[0].locations[0].items.remove(item)

    def remove_char(self, char: str):
        """
        Manually remove a character from this event.

        :param char: The char to remove.
        """
        if self._universe is None or self._timeline is None or self._location is None:
            raise ValueError("Need to follow UTL before removing char")

        if char not in self._chars:
            return
        self._chars.remove(char)
        self.current_event.universes[0].timelines[0].locations[0].characters.remove(char)
        
    def get_last_event(self, address: Optional[ParadoxAddress] = None) -> Event:
        """
        Get the last entered event that occurred at the given locality in paradox space.
        
        :return: The Event that occurred there.
        """
        location = timeline = univ = None

        if address is not None:
            if address.location != "":
                location = address.location
            if address.timeline != "":
                timeline = address.timeline
            if address.universe != "":
                univ = address.universe

        if location is None:
            location = self._location
        if timeline is None:
            timeline = self._timeline
        if univ is None:
            univ = self._universe
            
        found_event = None
        for evt in reversed(self._events):
            for u in evt.universes:
                if u.name == univ:
                    for tl in u.timelines:
                        if tl.path == timeline:
                            for loc in tl.locations:
                                if loc.path == location:
                                    found_event = evt
                                    break
                            if found_event is not None:
                                break
                    if found_event is not None:
                        break
            if found_event is not None:
                break
        
        return found_event

    def add_scene(self, location=None, timeline=None, universe=None):
        """
        Add a new UTL to the event, without disrupting the current one. If this is the first one to be added,
        it is immediately set as the currently followed one. Unlike in scene change, it is acceptable to create
        new upper level UTLs without specifying. The event will automatically bring in prior event items if possible
        (if as a result the operation a location is selected)

        :param location: The name of the location to add.
        :param timeline: The name of the timeline to add.
        :param universe: The name of the universe to add.
        """

        new_univ = False
        new_tl = False
        new_loc = False
        u = None
        t = None
        l = None

        if universe is not None and timeline is None and location is None:
            u = self.current_event.get_universe(ParadoxAddress(universe=universe))
            if u is not None:
                raise ValueError("Universe {!r} already exists".format(universe))
            u = Universe(name=universe)
            new_univ = True
        elif timeline is not None and location is None:
            if universe is None:
                if self._universe is None:
                    raise ValueError("No current universe so cannot infer it")
                u = self.current_event.universes[0]
            else:
                u = self.current_event.get_universe(ParadoxAddress(universe=universe))
                if u is None:
                    # defer adding to end of func in case somefin else goes wrong
                    new_univ = True
                    u = Universe(name=universe)

            t = u.get_timeline(timeline)
            if t is not None:
                raise ValueError("Timeline {!r} already exists in universe {!r}".format(timeline, u.name))

            t = Timeline(path=timeline)

        elif location is not None:
            if universe is None:
                if self._universe is None:
                    raise ValueError("No current universe so cannot infer it")
                u = self.current_event.universes[0]
            else:
                u = self.current_event.get_universe(ParadoxAddress(universe=universe))
                if u is None:
                    # defer adding to end of func in case somefin else goes wrong
                    new_univ = True
                    u = Universe(name=universe)

            if timeline is None:
                if self._timeline is None:
                    raise ValueError("No current timeline so cannot infer it")

                if new_univ:
                    t = Timeline(path=self._timeline)
                    new_tl = True
                else:
                    t = u.timelines[0]
            else:
                t = u.get_timeline(timeline)
                if t is None:
                    # defer adding to end of func in case somefin else goes wrong
                    new_tl = True
                    t = Timeline(path=timeline)

            if t.get_location(location) is None:
                l = Location(path=location)
                new_loc = True
            else:
                raise ValueError("Location {!r} already exists in timeline {!r}:{!r}".format(location, u.name, t.path))

        if new_loc:
            t.locations.append(l)
            if len(t.locations) == 1:
                self._location = l.path
        if new_tl:
            u.timelines.append(t)
            if len(u.timelines) == 1:
                self._timeline = t.path
        if new_univ:
            self.current_event.universes.append(u)
            if len(self.current_event.universes) == 1:
                self._universe = u.name

    def carry_over_scene(self, address: ParadoxAddress):
        scene = self.current_event.get_location(address)
        if scene is None:
            raise ValueError("Scene does not yet exist in this event: {!r}".format(address))

        last_event = self.get_last_event(address)
        if last_event is not None:
            loc_at_end = last_event.scene_at_end(address)
            self._items = set(loc_at_end.items)
            self._chars = set(loc_at_end.characters)
            self.current_event.universes[0].timelines[0].locations[0].characters.extend(loc_at_end.characters)
            self.current_event.universes[0].timelines[0].locations[0].items.extend(loc_at_end.items)

    def swap_scene(self, address: ParadoxAddress):
        address = address.copy()

        update_universe = update_timeline = update_location = None

        univ = None
        tl = None
        loc = None

        if address.has_universe():
            if address.universe_index < 0:
                # we need to do a search to get the new one
                idx = self.current_event.index_of_universe(address)
                if idx < 0:
                    raise ValueError("Universe {!r} does not exist".format(address.universe))
                address.universe_index = idx
            univ = self.current_event.get_universe(address)
            update_universe = address.universe_index != 0
        else:
            univ = self.current_event.universes[0]
            address.universe_index = 0
            address.universe = univ.name

        if address.has_timeline():
            if address.timeline_index < 0:
                # we need to do a search to get the new one
                idx = univ.index_of_timeline(address)
                if idx < 0:
                    raise ValueError("Timeline {!r} does not exist".format(address.timeline))
                address.timeline_index = idx
            tl = univ.get_timeline(address.timeline, address.timeline_index)
            update_timeline = address.timeline_index != 0
        else:
            tl = univ.timelines[0]
            address.timeline_index = 0
            address.timeline = tl.path

        if address.has_location():
            if address.location_index < 0:
                # we need to do a search to get the new one
                idx = tl.index_of_location(address)
                if idx < 0:
                    raise ValueError("Location {!r} does not exist".format(address.location))
                address.location_index = idx
            loc = tl.get_location(address.location, address.location_index)
            update_location = address.location_index != 0
        else:
            loc = tl.locations[0]
            address.location_index = 0
            address.location = loc.path

        if update_universe:
            del self.current_event.universes[address.universe_index]
            self.current_event.universes.insert(0, univ)
            self._universe = address.universe
        if update_timeline:
            del univ.timelines[address.timeline_index]
            univ.timelines.insert(0, tl)
            self._timeline = address.timeline
        if update_location:
            del tl.locations[address.location_index]
            tl.locations.insert(0, loc)
            self._location = address.location

    def scene_change(self, new_location, new_timeline=None, new_universe=None, preserve=False):
        """
        Completely wipe out the current event's scene and replace it with a new one, with default
        items and characters in it taken from the end of the last event that occured in this
        locality.

        :param new_location: The location to change to.
        :param new_timeline: The timeline to change to, if not given the current one is used.
        :param new_universe: The universe to change to, if not given the current one is used.
        :param preserve: If set to true, the current scene is saved and swapped to the next position
        in the Event instead of being replaced with the new one.
        """
        
        if new_timeline is not None:
            dest_timeline = new_timeline
        else:
            dest_timeline = self._timeline
            
        if new_universe is not None:
            dest_universe = new_universe
        else:
            dest_universe = self._universe
            
        if self._universe == dest_universe and self._timeline == dest_timeline and self._location == new_location:
            # we are already here. no need to change anyfin
            return
            
        if preserve:
            if dest_universe != self._universe:
                cur_univ = self.current_event.universes[0]
                self.current_event.universes.append(cur_univ.copy())
            elif dest_timeline != self._timeline:
                cur_timeline = self.current_event.universes[0].timelines[0]
                self.current_event.universes[0].timelines.append(cur_timeline.copy())
            elif new_location != self._location:
                cur_location = self.current_event.universes[0].timelines[0].locations[0]
                self.current_event.universes[0].timelines[0].locations.append(cur_location.copy())
        
        self._items = set()
        self._chars = set()

        dest_address = ParadoxAddress(location=new_location, timeline=dest_timeline, universe=dest_universe)
        self.carry_over_scene(dest_address)
        
        self._location = new_location
        self.current_event.universes[0].timelines[0].locations[0].path = new_location
        
        if new_timeline is not None:
            self._timeline = new_timeline
            self.current_event.universes[0].timelines[0].path = new_timeline
            
        if new_universe is not None:
            self._universe = new_universe
            self.current_event.universes[0].name = new_universe
            
        self.updated = True
        
    def next(self):
        self.goto(self._cursor + 1)
        
    def prev(self):
        self.goto(self._cursor - 1)
        
    def goto(self, cursor: int):
        if cursor < 0:
            raise ValueError("cursor needs to be >= 0")
        if cursor >= len(self._events):
            raise ValueError("cursor bigger than number of events")
            
        self._cursor = cursor
        
        event = self.current_event

        self._convo_participants = {}
        
        self._work = event.portrayed_in.work
        self._comic_page = event.portrayed_in.panel
               
        self._universe = None
        self._timeline = None
        self._location = None
        self._items = set()
        self._chars = set()
        if len(event.universes) > 0:
            self._universe = event.universes[0].name
            if len(event.universes[0].timelines) > 0:
                self._timeline = event.universes[0].timelines[0].path
                if len(event.universes[0].timelines[0].locations) > 0:
                    self._location = event.universes[0].timelines[0].locations[0].path
                    self._items = set(event.universes[0].timelines[0].locations[0].items)
                    self._chars = set(event.universes[0].timelines[0].locations[0].characters)

        if "convo" in event.meta:
            for m in event.meta:
                if m.startswith("convo:"):
                    char = m.split(":", 1)[1]
                    char_addr = event.address_of(char)
                    if char_addr is None:
                        raise ValueError("char {!r} is in convo but is not included in event universes".format(char))
                    self._convo_participants[char] = char_addr
        
    def advance_narrative(self, to_panel=0, for_dialog=False):
        if self._comic_page > to_panel:
            raise ValueError("advance needs to happen after the current for a narrative")
            
        if 0 < to_panel != self._comic_page + 1:
            self._comic_page = to_panel
            self._narrative_link = "causal"
        else:
            self._comic_page += 1
            self._narrative_link = "immediate"
    
        self._cursor = len(self._events)

        if for_dialog:
            portrayal = Citation("dialog", work=self._work, panel=self._comic_page)
        else:
            self._convo_participants = {}
            portrayal = Citation("narration", work=self._work, panel=self._comic_page)

        last_page_id = self._events[self._cursor - 1].id if self._cursor >= 1 else None
        last_page_link = Constraint("narrative_" + self._narrative_link, ref_event=last_page_id, is_after=True)
        loc = Location(path=self._location, characters=self._chars, items=self._items)
        tl = Timeline(path=self._timeline, locations=[loc])
        univ = Universe(path=self._universe, timelines=[tl])
        
        new_event = Event(portrayed_in=portrayal, constraints=[last_page_link], universes=[univ])
        self._events.append(new_event)
            
        self.updated = True
        
    def copy_events(self) -> List[Event]:
        return list(self._events)
        
    @property
    def current_event(self) -> Event:
        return self._events[self._cursor]
        
    @property
    def following(self) -> str:
        return self._following
        
    @following.setter
    def following(self, value: str):
        self._following = value
        
    @property
    def id(self) -> str:
        return self.current_event.id
        
    @property
    def name(self) -> str:
        return self.current_event.name
        
    @name.setter
    def name(self, value: str):
        self.current_event.name = value
            
        self.updated = True
        
    @property
    def description(self) -> str:
        return self.current_event.description
        
    @description.setter
    def description(self, value: str):
        self.current_event.description = value
            
        self.updated = True
        
    @property
    def work(self) -> str:
        return self._work
        
    @work.setter
    def work(self, value: str):
        self._work = value
        self.current_event.portrayed_in.work = value
            
        self.updated = True
        
    @property
    def universe(self) -> str:
        return self._universe
        
    @universe.setter
    def universe(self, value: str):
        self._universe = value
        self.current_event.universes[0].name = value
            
        self.updated = True
        
    @property
    def timeline(self) -> str:
        return self._timeline
        
    @timeline.setter
    def timeline(self, value: str):
        self._timeline = value
        self.current_event.universes[0].timelines[0].path = value
            
        self.updated = True
        
    @property
    def location(self) -> str:
        return self._location
        
    @location.setter
    def location(self, value: str):
        self._location = value
        self.current_event.universes[0].timelines[0].locations[0].path = value
            
        self.updated = True
        
    @property
    def comic_page(self) -> int:
        return self._comic_page
        
    @comic_page.setter
    def comic_page(self, value: int):
        self._comic_page = value
        self.current_event.portrayed_in.panel = value
    
    @property
    def items(self) -> List[str]:
        return list(self._items)
        
    @property
    def characters(self) -> List[str]:
        return list(self._chars)
